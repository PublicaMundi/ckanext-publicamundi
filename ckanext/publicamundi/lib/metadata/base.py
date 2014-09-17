import threading
import logging
import json
import itertools
import copy
import zope.interface
import zope.interface.verify
import zope.schema
from collections import namedtuple

from ckanext.publicamundi.lib import dictization
from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.util import stringify_exception
from ckanext.publicamundi.lib.json_encoder import JsonEncoder
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import \
    IObject, IErrorDict, ISerializer
from ckanext.publicamundi.lib.metadata import serializers
from ckanext.publicamundi.lib.metadata.serializers import \
    serializer_for_field, serializer_for_key_tuple

_cache = threading.local()

def flatten_schema(schema):
    '''Flatten an arbitrary zope-based schema.
    '''

    res = {}
    fields = zope.schema.getFields(schema)
    for k, field in fields.items():
        res1 = flatten_field(field)
        for k1, field1 in res1.items():
            res[(k,) +k1] = field1
    return res

def flatten_field(field):
    assert isinstance(field, zope.schema.Field)
    res = None
    
    if isinstance(field, zope.schema.Object):
        res = flatten_schema(field.schema)
    elif isinstance(field, (zope.schema.List, zope.schema.Tuple)):
        res = {}
        res1 = flatten_field(field.value_type)
        for i in range(0, field.max_length):
            for k1, field1 in res1.items():
                res[(i,) +k1] = field1
    elif isinstance(field, zope.schema.Dict):
        assert isinstance(field.key_type, zope.schema.Choice), \
            'Only zope.schema.Choice supported for key_type'
        res = {}
        res1 = flatten_field(field.value_type)
        for v in field.key_type.vocabulary:
            for k1, field1 in res1.items():
                res[(v.token,) +k1] = field1
    else:
        res = { (): field }
    
    return res

#
# Base implementation  
#

FieldContext = namedtuple('FieldContext', ['key', 'value'], verbose=False)

class Object(object):
    zope.interface.implements(IObject)

    ## interface IObject

    @classmethod
    def schema(cls):
        return cls.get_schema()

    def get_field(self, k):
        '''Return a bound field for attribute k'''
        schema = self.get_schema()
        v = getattr(self, k)
        return schema.get(k).bind(FieldContext(key=k, value=v))
    
    @classmethod
    def get_fields(cls):
        '''Return a map of fields for the zope schema of our class.
        '''

        res = zope.schema.getFields(cls.get_schema())
        return res

    @classmethod
    def get_flattened_fields(cls, opts={}):
        '''Return a map of flattened fields for the zope schema our class.
        '''
        
        res = flatten_schema(cls.get_schema())
        if opts.get('serialize-keys', False):
            kser = serializer_for_key_tuple()
            kser.prefix = opts.get('key-prefix', None)
            return { kser.dumps(k): field for k, field in res.iteritems() }
        else:
            return res

    def validate(self, dictize_errors=False):
        '''Validate against all known (schema-based or invariants) rules. 
        
        If dictize_errors is unset, return a list <errors> structured as:
          errors ::= [ (k, ef), ... ]
          ef ::= [ ex1, ex2, ...]
          ex ::= Invalid(arg0, arg1, ...)
          arg0 ::= errors
          arg0 ::= <literal-value>
        where:
          ef : field-errors
          ex : exception (derived from Invalid)
        
        If dictize_errors is set, the previous error list is attempted to
        be converted to a dict of errors (with keys corresponding to
        object's attributes or keys).

        '''

        cls = type(self)
        errors = cls.Validator(self).validate()
        if dictize_errors:
            return self.dictize_errors(errors)
        else:
            return errors

    def to_dict(self, flat=False, opts={}):
        if flat:
            serialize_keys = opts.get('serialize-keys', False)
            res = self.flatten(opts)
            if serialize_keys:
                kser = serializer_for_key_tuple()
                kser.prefix = opts.get('key-prefix', None)
                res = { kser.dumps(k): v for k, v in res.iteritems() }
        else:
            res = self.dictize(opts)
        return res

    def from_dict(self, d, is_flat=None, opts={}):
        assert isinstance(d, dict)
        cls = type(self)
        
        # Decide if input is a flattened dict
        
        if is_flat is None:
            is_flat = isinstance(d.iterkeys().next(), tuple)
        if is_flat:
            unserialize_keys = opts.get('unserialize-keys', False)
            if unserialize_keys:
                kser = serializer_for_key_tuple()
                kser.prefix = opts.get('key-prefix', None)
                d = dictization.unflatten({ 
                    kser.loads(k): v for k, v in d.iteritems() 
                })
            else:
                d = dictization.unflatten(d)
                
        # Load self
        
        self.load(d, opts)

        # Allow method chaining
        return self

    def to_json(self, flat=False, indent=None):
        cls = type(self)
        opts = {
            'serialize-keys': flat,
            'serialize-values': 'json-s',
        }
        d = self.to_dict(flat, opts)
        return json.dumps(d, indent=indent)

    def from_json(self, s, is_flat=False):
        cls = type(self)
        d = json.loads(s)
        opts = {
            'unserialize-keys': is_flat,
            'unserialize-values': 'json-s',
        }
        return self.from_dict(d, is_flat, opts=opts)
    
    ## Constructor based on keyword args 

    def __init__(self, **kwargs):
        cls = type(self)
        schema = cls.get_schema()
        for k,field in zope.schema.getFields(schema).items():
            a = getattr(cls, k)
            if isinstance(a, property):
                continue
            if kwargs.has_key(k):
                v = kwargs.get(k)
            else:
                factory = cls.get_field_factory(k, field)
                v = factory() if factory else field.default
            setattr(self, k, v)

    ## Provide a string representation

    def __repr__(self):
        cls = type(self)
        typename = cls.__name__ #"%s:%s" %(cls.__module__, cls.__name__)
        s = '<' + typename
        for k,field in self.get_fields().items():
            f = field.get(self)
            if f:
                s += ' %s=%s' %(k, repr(f))
        s += '>'
        return s

    ## Introspective helpers

    @classmethod
    def _determine_schema(cls):
        schema = None
        for iface in zope.interface.implementedBy(cls):
            if iface.extends(IObject):
                schema = iface
                break
        return schema

    @classmethod
    def get_schema(cls):
        schema = None
        if not hasattr(_cache, 'schema'):
            _cache.schema = {}
        try:
            schema = _cache.schema[cls]
        except KeyError:
            schema  = cls._determine_schema()
            _cache.schema[cls] = schema
        return schema

    @classmethod
    def get_field_names(cls):
        schema = cls.get_schema()
        return zope.schema.getFieldNames(schema) 
         
    @classmethod
    def get_field_factory(cls, k, field=None):
        assert not k or isinstance(k, basestring)
        assert not field or isinstance(field, zope.schema.Field)
        assert k or field, 'At least one of {k, field} should be specified'
        
        factory = None
        
        # Check if a factory is defined explicitly as a class attribute
        if k and hasattr(cls, k):
            a = getattr(cls, k)
            if callable(a):
                factory = a
                return factory
            else:
                return None
        
        # If reached here, there is no hint via class attribute. 
        # Try to find a factory for this field.
        if not field:
            schema = cls.get_schema()
            field = schema.get(k)
            if not field:
                raise ValueError('No field %s for schema %s' %(k, schema))
        if isinstance(field, zope.schema.Object):
            factory = adapter_registry.lookup([], field.schema)
        else:
            factory = field.defaultFactory
        
        return factory

    ## Validation 

    class Validator(object):

        def __init__(self, obj, opts=None):
            self.obj = obj
            self.opts = opts or {}
            return

        def validate(self):
            '''Return <errors> following the structure of Object.validate() result'''
            errors = self.validate_schema()
            if errors:
                # Stop here, do not check invariants
                return errors
            else:
                return self.validate_invariants()

        def validate_schema(self):
            '''Return <errors>'''
            schema = self.obj.get_schema()
            errors = []
            for k, field in zope.schema.getFields(schema).items():
                f = field.get(self.obj)
                ef = self._validate_schema_for_field(f, field)
                if ef:
                    errors.append((k, ef))
            return errors

        def _validate_schema_for_field(self, f, field):
            '''Return <ef>, i.e. an array of field-specific exceptions'''
            ef = []
            # Check if empty
            if f is None:
                # Check if required
                try:
                    field.validate(f)
                except zope.interface.Invalid as ex:
                    ef.append(ex)
                return ef
            # If here, we are processing an non-empty field
            if isinstance(field, zope.schema.Object):
                # Check interface is provided by instance f 
                try:
                    zope.interface.verify.verifyObject(field.schema, f)
                except zope.interface.Invalid as ex:
                    ef.append(ex)
                # If provides, descend into object's schema validation
                if not ef and isinstance(f, Object):
                    cls = type(self)
                    # Note: Here, maybe we should just validate().
                    # It depends on if we consider a failed invariant on a 
                    # field as a schema error on our level. 
                    errors = cls(f, self.opts).validate_schema()
                    if errors:
                        ef.append(zope.interface.Invalid(errors))
            elif isinstance(field, (zope.schema.List, zope.schema.Tuple)):
                # Check is a list type
                if not (isinstance(f, list) or isinstance(f, tuple)):
                    try:
                        field.validate(f)
                    except zope.interface.Invalid as ex:
                        ef.append(ex)
                # If type is ok, proceed to schema validation
                if not ef:
                    exs = self._validate_schema_for_field_items(enumerate(f), field)
                    if exs:
                        ef.extend(exs)
            elif isinstance(field, zope.schema.Dict):
                # Check is a dict type
                if not isinstance(f, dict):
                    try:
                        field.validate(f)
                    except zope.interface.Invalid as ex:
                        ef.append(ex)
                # If type is ok, proceed to schema validation
                if not ef:
                    exs = self._validate_schema_for_field_items(f.iteritems(), field)
                    if exs:
                        ef.extend(exs)
            else:
                # A leaf field: validate directly via Field
                try:
                    field.validate(f)
                except zope.interface.Invalid as ex:
                    ef.append(ex)
            return ef

        def _validate_schema_for_field_items(self, items, field):
            '''Return list of <ex> i.e. a list of Invalid-based exceptions'''
            exs = []
            # Hydrate items (must be re-used)
            items = list(items)

            # 1. Validate length contraints
            if field.min_length and len(items) < field.min_length:
                exs.append(zope.schema.interfaces.TooShort(
                    'The collection is too short (< %d)' % (field.min_length)))
            
            if field.max_length and len(items) > field.max_length:
                exs.append(zope.schema.interfaces.TooBig(
                    'The collection is too big (> %d)' % (field.max_length)))

            # 2. Validate items
            errors = []
            # 2.1 Validate item keys (if exist)
            if hasattr(field, 'key_type') and field.key_type:
                assert isinstance(field.key_type, zope.schema.Choice)
                for k,y in items:
                    try:
                        field.key_type.validate(k)
                    except zope.interface.Invalid as ex:
                        errors.append((k, [ex]))
                pass
            # 2.2 Validate item values
            for k,y in items:
                ef = self._validate_schema_for_field(y, field.value_type)
                if ef:
                    errors.append((k, ef))
            if errors:
                exs.append(zope.interface.Invalid(errors))

            return exs

        def validate_invariants(self):
            '''Return <errors>'''
            errors = []
            schema = self.obj.get_schema()

            # Descend into field invariants
            recurse = False
            try:
                recurse = schema.getTaggedValue('recurse-on-invariants')
            except KeyError:
                pass
            if recurse:
                for k, field in zope.schema.getFields(schema).items():
                    f = field.get(self.obj)
                    if not f:
                        continue
                    ef = self._validate_invariants_for_field(f, field)
                    if ef:
                        errors.append((k, ef))

            # Check own invariants
            try:
                ef = []
                schema.validateInvariants(self.obj, ef)
            except zope.interface.Invalid:
                errors.append((None, ef))

            return errors

        def _validate_invariants_for_field(self, f, field):
            '''Returns <ef>, i.e. an array of field-specific exceptions'''
            ef = []

            ex  = None
            if isinstance(field, zope.schema.Object):
                cls = type(self)
                errors = cls(f, self.opts).validate_invariants()
                if errors:
                    ex = zope.interface.Invalid(errors)
            elif isinstance(field, (zope.schema.List, zope.schema.Tuple)):
                ex = self._validate_invariants_for_field_items(enumerate(f), field)
            elif isinstance(field, zope.schema.Dict):
                ex = self._validate_invariants_for_field_items(f.iteritems(), field)

            if ex:
                ef.append(ex)
            return ef

        def _validate_invariants_for_field_items(self, items, field):
            '''Return <ex> i.e. an Invalid-based exception'''
            ex = None
            
            errors = []
            for k,y in items:
                ef = self._validate_invariants_for_field(y, field.value_type)
                if ef:
                    errors.append((k, ef))
            
            if errors:
                ex = zope.interface.Invalid(errors)
            return ex    

    ## Error helpers - Convert error lists 

    def dictize_errors(self, errors):
        '''Convert an <errors> structure to a nested dict (wrapped inside an ErrorDict)'''
        return self._dictize_errors(errors)

    def _dictize_errors(self, errors):
        global_key = ErrorDict.global_key
        schema = self.get_schema()
        res = ErrorDict()
        for k, ef in errors:
            if k is None:
                # Found failed invariants
                res[global_key] = [ str(ex) for ex in ef ]
            else:
                # Found a field-level error
                field = schema.get(k)
                if not field:
                    continue
                f = field.get(self)
                res[k] = self._dictize_errors_for_field(ef, f, field)
        return res

    def _dictize_errors_for_field(self, ef, f, field):
        '''Build a result for field-level errors from an <ef> structure.
        This can be either a list of strings (leaf case) or a dict (non-leaf case)
        '''
        
        assert all([ isinstance(ex, zope.interface.Invalid) for ex in ef ])
         
        # Decide if this result should be represented by a dict (non-leaf)
        # or by a simple list of error strings (leaf).
        # When fine-grained error info exists on subfields (i.e. when an
        # exception with 1st arg an array of <errors> is encountered), then
        # we must a use a dict. Otherwise, we simply use a array of strings.

        are_leafs = [ not(ex.args and isinstance(ex.args[0], list)) for ex in ef ]
        
        if all(are_leafs):
            # Treat as literal strings, stop descending
            return [ stringify_exception(ex) for ex in ef ]
        
        # If here, we must descend (at least once) to field-level errors    
        
        global_key = ErrorDict.global_key

        res = None
        if isinstance(field, zope.schema.Object):
            res = ErrorDict()
            if not isinstance(f, Object):
                # Return array of exceptions as is (cannot descend into object)
                return ef
            # It supports further dictization, descent into object
            for ex, is_leaf in itertools.izip(ef, are_leafs):
                if is_leaf:
                    if not global_key in res:
                        res[global_key] = []
                    res[global_key].append(stringify_exception(ex))
                else:
                    # Recurse on an <errors> structure (ex.args[0])
                    res1 = f._dictize_errors(ex.args[0])
                    res = dictization.merge_inplace(res, res1) 
        elif isinstance(field, (zope.schema.List, zope.schema.Tuple, zope.schema.Dict)):
            res = ErrorDict()
            for ex, is_leaf in itertools.izip(ef, are_leafs): 
                if is_leaf:
                    if not global_key in res:
                        res[global_key] = []
                    res[global_key].append(stringify_exception(ex))
                else:
                    # Recurse on an <errors> structure (ex.args[0])
                    res1 = self._dictize_errors_for_field_collection(ex.args[0], f, field)
                    res = dictization.merge_inplace(res, res1) 
        else:
            # This is a field that is not composite (does not contain subfields)
            res = [ stringify_exception(ex) for ex in ef ]

        return res

    def _dictize_errors_for_field_collection(self, errors, f, field):
        res = ErrorDict()
        for k, ef in errors:
            # Here, k will be either an integer or a string
            res[k] = self._dictize_errors_for_field(ef, f[k], field.value_type)
        return res

    def flatten_errors(self, errors):
        ''' Convert an <errors> structure to a flattened dict '''
        error_dict = self._dictize_errors(errors)
        return dictization.flatten(error_dict)

    ## Dictization helpers

    class Dictizer(object):
        
        max_depth = 16

        def __init__(self, obj, opts={}):
            self.obj = obj
            self.opts = opts

        def dictize(self):
            obj = self.obj
            obj_cls = type(obj)
            schema = obj_cls.get_schema()
            
            max_depth = self.opts.get('max-depth', self.max_depth) 
            assert max_depth > 0
            
            fields = zope.schema.getFields(schema)
            res = {}
            for k, field in fields.items():
                a = getattr(obj_cls, k)
                if isinstance(a, property):
                    continue
                f = field.get(obj)
                if f is None:
                    res[k] = None
                else:
                    res[k] = self._dictize_field(f, field, max_depth -1)
            
            return res

        def _get_field_value(self, f, field):
            '''Get the value of a field considered as a leaf.
            Serialize this value if requested so.
            '''
            v = f
            fmt = self.opts.get('serialize-values', False)
            if (v is not None) and fmt:
                fmt = 'default' if isinstance(fmt, (bool, int)) else str(fmt)
                ser = serializer_for_field(field, fmt=fmt)
                if ser:
                    try:
                        v = ser.dumps(f)
                    except:
                        v = None
            return v

        def _dictize_field(self, f, field, max_depth):
            
            if max_depth == 0:
                return self._get_field_value(f, field)
            
            # Descend into this field
            
            dictize_field = self._dictize_field

            if isinstance(field, zope.schema.Object):
                if isinstance(f, Object):
                    cls = type(self)
                    opts = copy.copy(self.opts)
                    opts['max-depth'] = max_depth
                    return cls(f, opts).dictize()
                else:
                    # Handle only derivatives of Object
                    return None
            elif isinstance(field, (zope.schema.List, zope.schema.Tuple)):
                return [ dictize_field(y, field.value_type, max_depth -1) 
                    for y in f ]
            elif isinstance(field, zope.schema.Dict):
                return { k: dictize_field(y, field.value_type, max_depth -1) 
                    for k,y in f.items() } 
            else:
                # Handle a leaf field 
                return self._get_field_value(f, field)

        def flatten(self):
            obj = self.obj
            obj_cls = type(obj)
            schema = obj_cls.get_schema()

            max_depth = self.opts.get('max-depth', self.max_depth) 
            assert max_depth > 0

            fields = zope.schema.getFields(schema)
            res = {}
            for k, field in fields.items():
                a = getattr(obj_cls, k)
                if isinstance(a, property):
                    continue
                f = field.get(obj)
                if f is None:
                    pass
                else:
                    res1 = self._flatten_field(f, field, max_depth -1)
                    for k1,v1 in res1.items():
                        res[(k,) +k1] = v1
            
            return res

        def _flatten_field(self, f, field, max_depth):
            
            if max_depth == 0:
                v = self._get_field_value(f, field)
                return { (): v }
            
            # Descend into this field
           
            if isinstance(field, zope.schema.Object):
                if isinstance(f, Object):
                    cls = type(self)
                    opts = copy.copy(self.opts)
                    opts['max-depth'] = max_depth
                    return cls(f, opts).flatten()
                else:
                    # Handle only derivatives of Object
                    return None
            elif isinstance(field, (zope.schema.List, zope.schema.Tuple)):
                return self._flatten_field_items(enumerate(f), field, max_depth)
            elif isinstance(field, zope.schema.Dict):
                return self._flatten_field_items(f.iteritems(), field, max_depth)
            else:
                # Handle a leaf field
                v = self._get_field_value(f, field)
                return { (): v }

        def _flatten_field_items(self, items, field, max_depth):
            res = dict()
            for k, y in items:
                yres = self._flatten_field(y, field.value_type, max_depth -1)
                for yk, yv in yres.iteritems():
                    res[(k,) +yk] = yv
            return res

    class Loader(object):

        def __init__(self, obj, opts={}):
            self.obj = obj
            self.opts = opts

        def load(self, data):
            obj = self.obj
            obj_cls = type(obj)

            schema = obj_cls.get_schema()
            fields = zope.schema.getFields(schema)
            for k, field in fields.items():
                a = getattr(obj_cls, k)
                if isinstance(a, property):
                    continue
                v = data.get(k)
                factory = obj.get_field_factory(k, field)
                f = None
                if v is None:
                    # No value given, use factory (if exists)
                    f = factory() if factory else field.default
                else:
                    # An input was provided for k
                    f = self._create_field(v, field, factory)
                setattr(obj, k, f)

            return

        def _create_field(self, v, field, factory=None):
            assert isinstance(field, zope.schema.Field)
            cls = type(self)

            # Find a factory (if not supplied)
            if not factory:
                factory = self.obj.get_field_factory(None, field)
            
            # Create a new field instance

            if isinstance(field, zope.schema.Object):
                if isinstance(v, dict):
                    # Load from a dict
                    f = factory()
                    if isinstance(f, Object):
                        cls(f, self.opts).load(v)
                    else:
                        # Handle only derivatives of Object
                        pass
                else:
                    # The supplied value is not a dict, so we cannot invoke Loader
                    # (maybe product of a depth-limited dictization). Assign it.
                    f = v 
                    pass
                return f
            elif isinstance(field, (zope.schema.List, zope.schema.Tuple)):
                return [ self._create_field(y, field.value_type)
                    for y in v ]
            elif isinstance(field, zope.schema.Dict):
                return { k: self._create_field(y, field.value_type)
                    for k, y in v.iteritems() }
            else:
                # Handle a leaf field (may need to be unserialized)
                f = v
                fmt = self.opts.get('unserialize-values', False)
                if (f is not None) and fmt:
                    fmt = 'default' if isinstance(fmt, (bool, int)) else str(fmt)
                    ser = serializer_for_field(field, fmt=fmt)
                    if ser:
                        try:
                            f = ser.loads(v)
                        except:
                            f = None
                return f

    class Factory(object):

        def __init__(self, iface, opts={}):
            if not iface.extends(IObject): 
                raise ValueError('Expected an interface based on IObject')
            self.target_iface = iface
            self.target_cls = adapter_registry.lookup([], iface, '')
            if not self.target_cls:
                raise ValueError('Cannot find an implementation for %s' %(iface))
            
            self.opts = {
                'unserialize-values': False,
            }
            self.opts.update(opts)

        def from_dict(self, d, is_flat=False):
            return self.target_cls().from_dict(d, is_flat, self.opts)

        def __call__(self, d={}, is_flat=False):
            return self.from_dict(d, is_flat)

    def dictize(self, opts=None):
        cls = type(self)
        return cls.Dictizer(self, opts).dictize()

    def flatten(self, opts=None):
        cls = type(self)
        return cls.Dictizer(self, opts).flatten()

    def load(self, d, opts=None):
        cls = type(self)
        return cls.Loader(self, opts).load(d)

class ErrorDict(dict):
    '''Provide a simple dict for validation errors.
    '''
    zope.interface.implements(IErrorDict)

    global_key = '__after'

#
# Serializers
#

@serializers.object_serialize_adapter(IObject, fmt='default')
class ObjectSerializer(serializers.BaseSerializer):
    '''Provide a simple serializer (to JSON string) for derivatives of Object
    '''

    def __init__(self, obj):
        self.obj = obj
    
    def dumps(self, o=None):
        if o is None:
            o = self.obj
        assert isinstance(o, Object)
        return o.to_json()
        
    def loads(self, s):
        factory = type(self.obj)
        return factory().from_json(s)

def serializer_for_object(obj):
    '''Get a proper serializer for an Object instance.
    ''' 
    assert isinstance(obj, Object)
    serializer = adapter_registry.queryMultiAdapter(
        [obj], ISerializer, 'serialize:default')
    return serializer

