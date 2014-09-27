import threading
import logging
import json
import itertools
import copy
import zope.interface
import zope.interface.verify
import zope.schema

from ckanext.publicamundi.lib import dictization
from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.util import stringify_exception
from ckanext.publicamundi.lib.memoizer import memoize
from ckanext.publicamundi.lib.json_encoder import JsonEncoder
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import (
    IObject, IErrorDict, ISerializer, IFormatter, IFormatSpec)
from ckanext.publicamundi.lib.metadata.fields import IObjectField
from ckanext.publicamundi.lib.metadata import formatters
from ckanext.publicamundi.lib.metadata.formatters import (
    formatter_for_field, field_format_adapter, 
    BaseFormatter, BaseFieldFormatter, FormatSpec)
from ckanext.publicamundi.lib.metadata import serializers
from ckanext.publicamundi.lib.metadata.serializers import (
    serializer_for_field, serializer_for_key_tuple, BaseSerializer)

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

class FieldContext(object):

    __slots__ = ('key', 'value', 'title')

    def __init__(self, key, value, title=None):
        self.key = key
        self.value = value
        self.title = title
    
    def __repr__(self):
        return u'%s(key=%r, value=%r, title=%r)' % (
            self.__class__.__name__,
            self.key, self.value, self.title)

class Object(object):
    
    zope.interface.implements(IObject)

    ## interface IObject

    @classmethod
    @memoize
    def get_schema(cls):
        '''Get the underlying zope schema for this class.
        '''
        return cls._determine_schema()

    def get_field(self, k):
        '''Return a bound field for a key k.

        Note that, depending on it's type, k will be interpeted as:  
            * as an direct attribute of this object, if a string
            * as a path of attributes/indices/keys inside this object, if a tuple
        '''
        if isinstance(k, basestring):
            kt = (k,)
        else:
            kt = tuple(k)

        field, val = self._get_field(kt)
        return field

    @classmethod
    def get_fields(cls, exclude_properties=False):
        '''Return a map of fields for the zope schema of our class.
        ''' 
        return dict(cls.iter_fields(exclude_properties))
 
    @classmethod
    def iter_fields(cls, exclude_properties=False):
        '''Iterate on (key, field)
        '''
        schema = cls.get_schema()
        fields = zope.schema.getFields(schema).iteritems()
        if not exclude_properties:
            for k, field in fields:
                yield k, field
        else:
            for k, field in fields:
                a = getattr(cls, k)
                if isinstance(a, property):
                    continue
                yield k, field

    @classmethod
    def get_flattened_fields(cls, opts={}):
        '''Return a map of flattened fields for the zope schema our class.
        '''
        
        schema = cls.get_schema()
        res = flatten_schema(schema)
        if opts.get('serialize-keys', False):
            kser = serializer_for_key_tuple(opts.get('key-prefix'))
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
        '''Convert to a (flat or nested) dict.
        
        The supported options (opts) are:
            * serialize-keys: bool (default: False)
                Indicate whether we want our keys to be serialized. Of course,
                this has no effect if we ask for a nested dict. 
            * key-prefix: str (default: None)
                The string prefix for keys if they are to be serialized.
            * max-depth: int (None)
                Specify the maximum depth to dive into.
            * serialize-values: bool, str (default: False)
                Indicate whether we want our values to be serialized. If this 
                option is given as a string, will be interpreted as a serialization
                format (see serializers.supported_formats).
            * format-values: bool, str, FormatSpec (default: False)
                Indicate whether we want our values to be formatted. Note that this
                option cannot co-exist with `serialize-values`. If given as a string,
                will be interpreted as a format-specifier (see formatters.FormatSpec).
        '''

        # Preprocess and sanitize opts
        
        format_values = opts.get('format-values', False)
        serialize_values = opts.get('serialize-values', False)

        if format_values and serialize_values:
            raise ValueError(
                'The options `format-values` and `serialize-values` are incompatible.')
        
        opts = copy.copy(opts) # will modify it ...

        if format_values:
            if isinstance(format_values, FormatSpec):
                pass
            elif isinstance(format_values, (bool, int)):
                format_values = FormatSpec(name='default', opts={})
            else:
                format_values = FormatSpec.parse(str(format_values))
            opts['format-values'] = format_values
        elif serialize_values:     
            if isinstance(serialize_values, (bool, int)):
                serialize_values = 'default'
            else:
                serialize_values = str(serialize_values)
            opts['serialize-values'] = serialize_values

        # Dictize
        
        if flat:
            serialize_keys = opts.get('serialize-keys', False)
            res = self.flatten(opts)
            if serialize_keys:
                kser = serializer_for_key_tuple(opts.get('key-prefix'))
                res = { kser.dumps(k): v for k, v in res.iteritems() }
        else:
            res = self.dictize(opts)
        
        return res

    def from_dict(self, d, is_flat=None, opts={}):
        '''Convert (i.e. load) from a (flat or nested) dict.
        
        The supported options (opts) are:
            * unserialize-keys: bool (default: False)
                Indicate whether keys need to be unserialized before anything else
                happens. This option has no effect if we are loading from a nested dict.
            * key-prefix: str (default: None)
                The string prefix for keys if they are to be unserialized.
            * unserialize-values: str (default: False)
                Indicate whether values are to unserialized. If given as a string, will be
                interpreted as a serialization format (see serializers.supported_formats)
        '''

        assert isinstance(d, dict)
        cls = type(self)
        
        # Preprocess and sanitize opts

        opts = copy.copy(opts) # will modify it    

        unserialize_values = opts.get('unserialize-values', False)
        if unserialize_values:
            if isinstance(unserialize_values, (bool, int)):
                unserialize_values = 'default'
            else:
                unserialize_values = str(unserialize_values)
            opts['unserialize-values'] = unserialize_values

        # Decide if input is a flattened dict
        
        if is_flat is None:
            is_flat = isinstance(d.iterkeys().next(), tuple)
        if is_flat:
            unserialize_keys = opts.get('unserialize-keys', False)
            if unserialize_keys:
                kser = serializer_for_key_tuple(opts.get('key-prefix'))
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
    
    ## Constructor

    def __init__(self, **kwargs):
        '''Provide a constructor based on keyword args.

        Note: This constructor will ignore properties equiped with setter methods 
        (i.e. non-readonly properties). 
        '''

        cls = type(self)
        for k, field in cls.iter_fields(exclude_properties=True):
            if kwargs.has_key(k):
                v = kwargs.get(k)
            else:
                factory = cls.get_field_factory(k, field)
                v = factory() if factory else field.default
            setattr(self, k, v)

    ## Formatters / Representers

    def __repr__(self):
        '''Provide a string representation for an object.
        '''
        cls = type(self)
        
        argv = list()
        for k, field in cls.iter_fields(exclude_properties=True):
            f = field.get(self)
            if f is not None:
                argv.append((k, repr(f)))
        
        args = ', '.join(map(lambda t: '%s=%s' % t, argv))
        r = '%s(%s)' % (cls.__name__, args)
        return r

    def __format__(self, format_spec):
        '''Provide support for the native formatting mechanism. 
        This merely parses format_spec string and invokes a formatter (if found)
        with the proper args.
        '''
        
        p = FormatSpec.parse(format_spec)
        fo = formatter_for_object(self, p.name)
        return fo.format(self, p.opts) if fo else repr(self)

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

    ## Field accessors 
    
    def _get_field(self, kt):
        
        k, kt = kt[0], kt[1:]
        schema = self.get_schema()
        field = schema.get(k)
        value = getattr(self, k)
        
        if kt:
            return self._get_field_field(field, value, kt)
        else:
            yf = field.bind(FieldContext(key=k, value=value))
            yf.context.title = yf.title
            return (yf, value)
    
    def _get_field_field(self, field, value, kt):
        
        assert kt

        # Descend

        yf = yv = None

        more = (len(kt) > 1)
        
        if isinstance(field, zope.schema.Object):
            if not field.schema.extends(IObject):
                raise ValueError(
                    'Unknown structure (not an IObject) at field %r' % (field))
            if not field.schema.providedBy(value):
                raise ValueError('The object at field %r is invalid' % (field))
            yf, yv = value._get_field(kt)
        elif isinstance(field, (zope.schema.List, zope.schema.Tuple)):
            if not isinstance(value, (list, tuple)):
                raise ValueError(
                    'Invalid structure (not a list or tuple) at %r' % (field))
            iv = int(kt[0])
            yv = value[iv]
            if more:
                yf, yv = self._get_field_field(field.value_type, yv, kt[1:])
            else:
                yf = field.value_type.bind(FieldContext(key=iv, value=yv))
                yf.context.title = u'%s #%d' % (yf.title, iv)
        elif isinstance(field, zope.schema.Dict):
            if not isinstance(value, dict):
                raise ValueError(
                    'Invalid structure (not a dict) at %r' % (field))
            kv = str(kt[0])
            yv = value[kv]
            if more:
                yf, yv = self._get_field_field(field.value_type, yv, kt[1:])
            else:
                yf = field.value_type.bind(FieldContext(key=kv, value=yv))
                kn = field.key_type.vocabulary.getTerm(kv).title
                yf.context.title = u'%s - %s' %(yf.title, kn)
        else:
            raise ValueError('The key path cannot be consumed: %r' % (kt))
        
        return yf, yv

    ## Validation 

    class Validator(object):

        __slots__ = ('obj', 'opts')
        
        def __init__(self, obj, opts=None):
            self.obj = obj
            self.opts = opts or {}
            return

        def validate(self):
            '''Return <errors> following the structure of the result documented at 
            Object.validate().
            '''
            errors = self.validate_schema()
            if errors:
                # Stop here, do not check invariants
                return errors
            else:
                return self.validate_invariants()

        def validate_schema(self):
            '''Return <errors>'''
            errors = []
            
            obj = self.obj
            for k, field in obj.iter_fields():
                f = field.get(obj)
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
                    # Note: Here, maybe we should just validate(). It depends on if
                    # we consider a failed invariant on a field as a schema error 
                    # on our level. 
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

            obj = self.obj
            schema = obj.get_schema()

            # Descend into field invariants
            
            recurse = False
            try:
                recurse = schema.getTaggedValue('recurse-on-invariants')
            except KeyError:
                pass
            if recurse:
                for k, field in obj.iter_fields():
                    f = field.get(obj)
                    if not f:
                        continue
                    ef = self._validate_invariants_for_field(f, field)
                    if ef:
                        errors.append((k, ef))

            # Check own invariants
            
            try:
                ef = []
                schema.validateInvariants(obj, ef)
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

    ## Dictization

    class Dictizer(object):
        
        __slots__ = ('obj', 'opts', 'max_depth')
        
        max_depth = 16

        def __init__(self, obj, opts={}):
            '''Create a dictizer for an object.

            All received opts may be considered sanitized.
            '''
            self.obj = obj
            self.opts = opts

        def dictize(self):
            obj = self.obj
            
            max_depth = self.opts.get('max-depth', self.max_depth) 
            assert max_depth > 0
            
            res = {}
            for k, field in obj.iter_fields(exclude_properties=True):
                f = field.get(obj)
                if f is None:
                    res[k] = None
                else:
                    res[k] = self._dictize_field(f, field, max_depth -1)
            
            return res

        def _is_field_accessible(self, field):
            
            format_spec = self.opts.get('format-values')
            if format_spec:
                # Check if this field allows us to descend in order to format it's
                # parts (or stop here and format it as a whole).
                fo_conf = formatters.config_for_field(field, format_spec.name)
                return fo_conf.get('descend-if-dictized', True) if fo_conf else True
            else:
                # No formatting takes place
                return True
        
        def _get_field_value(self, v, field):
            '''Get the value of a field considered a leaf.
            Serialize or format (not both!) this value, if requested so.
            '''
            assert v is not None, 'This was supposed to be checked at dictize()'
            
            # Check if value needs to be serialized

            serializer_name = self.opts.get('serialize-values', False)
            if serializer_name:
                ser = serializer_for_field(field, serializer_name)
                if ser:
                    try:
                        v = ser.dumps(v)
                    except:
                        logger.warn(
                            'Failed to serialize value %r for field %r (%s)' % (
                                v, field.__name__, field.__class__.__name__))
                        v = None
                # Return here, no need to do anything more
                return v
            
            # Check if value needs to be formatted 
            
            format_spec = self.opts.get('format-values', False)
            if format_spec:
                assert isinstance(format_spec, FormatSpec)
                fo = formatter_for_field(field, format_spec.name)
                if fo:
                    fo_opts = format_spec.opts
                    # Fetch any extra field-level extra options
                    fo_conf = formatters.config_for_field(field, format_spec.name)
                    if fo_conf and 'extra-opts' in fo_conf:
                        fo_opts = copy.copy(fo_opts)
                        fo_opts.update(fo_conf.get('extra-opts'))
                    # Try to format
                    try:
                        v = fo.format(v, opts=fo_opts)
                    except:
                        logger.warn(
                            'Failed to format value %r for field %r (%s)' % (
                                v, field.__name__, field.__class__.__name__))
                        v = None
            
            return v

        def _dictize_field(self, f, field, max_depth):
            
            if max_depth == 0 or not self._is_field_accessible(field):
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

            max_depth = self.opts.get('max-depth', self.max_depth) 
            assert max_depth > 0

            res = {}
            for k, field in obj.iter_fields(exclude_properties=True):
                f = field.get(obj)
                if f is None:
                    pass
                else:
                    res1 = self._flatten_field(f, field, max_depth -1)
                    for k1,v1 in res1.items():
                        res[(k,) +k1] = v1
            
            return res

        def _flatten_field(self, f, field, max_depth):
            
            if max_depth == 0 or not self._is_field_accessible(field):
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
        
        __slots__ = ('obj', 'opts')

        def __init__(self, obj, opts={}):
            '''Create a loader for an object.

            All received opts may be considered sanitized.
            '''
            self.obj = obj
            self.opts = opts

        def load(self, data):
            obj = self.obj

            for k, field in obj.iter_fields(exclude_properties=True):
                v = data.get(k)
                factory = obj.get_field_factory(k, field)
                f = None
                if v is None:
                    # No value given, use factory (if available)
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
                assert f is not None, 'This was supposed to be checked at load()'
                serializer_name = self.opts.get('unserialize-values', False)
                if serializer_name:
                    ser = serializer_for_field(field, serializer_name)
                    if ser:
                        try:
                            f = ser.loads(f)
                        except:
                            logger.warn(
                                'Failed to unserialize value %r for field %r (%s)' % (
                                    f, field.__name__, field.__class__.__name__))
                            f = None
                return f

    class Factory(object):

        __slots__ = ('opts', 'target_iface', 'target_factory')
        
        def __init__(self, iface, opts={}):
            if not iface.extends(IObject): 
                raise ValueError('Expected an interface based on IObject')
            
            self.target_iface = iface
            self.target_factory = adapter_registry.lookup([], iface, '')
            if not self.target_factory:
                raise ValueError('Cannot find an implementor for %s' %(iface))
            
            self.opts = {
                'unserialize-values': False,
            }
            self.opts.update(opts)

        def from_dict(self, d, is_flat=False):
            obj = self.target_factory()
            return obj.from_dict(d, is_flat, self.opts)

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
# Named adapters (implementers)
#

def object_null_adapter(name=''):
    def decorate(cls):
        assert issubclass(cls, Object)
        provided_iface = cls.get_schema()
        adapter_registry.register([], provided_iface, name, cls)
        return cls
    return decorate

#
# Serializers
#

def object_serialize_adapter(required_iface, name='default'):
    assert required_iface.isOrExtends(IObject)
    assert name in serializers.supported_formats
    def decorate(cls):
        adapter_registry.register(
            [required_iface], ISerializer, 'serialize:%s' %(name), cls)
        return cls
    return decorate

@object_serialize_adapter(IObject, 'default')
class ObjectSerializer(BaseSerializer):
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

def serializer_for_object(obj, name='default'):
    '''Get a proper serializer for an Object instance.
    ''' 
    assert name in serializers.supported_formats
    
    serializer = adapter_registry.queryMultiAdapter(
        [obj], ISerializer, 'serialize:%s' %(name))
    return serializer

#
# Formatters
# 

@field_format_adapter(IObjectField, 'default')
class ObjectFieldFormatter(BaseFieldFormatter):
    
    def _format(self, obj, opts):
        fo = formatter_for_object(obj)
        return fo.format(obj, opts) if fo else format(obj)
        
def object_format_adapter(required_iface, name='default'):
    assert required_iface.isOrExtends(IObject)
    assert name in formatters.supported_formats
    def decorate(cls):
        adapter_registry.register(
            [required_iface], IFormatter, 'format:%s' %(name), cls)
        return cls
    return decorate

@object_format_adapter(IObject, 'default')
class ObjectFormatter(BaseFormatter):
    '''Provide a simple formatter for derivatives of Object.
    '''

    def __init__(self, obj):
        self.obj = obj
    
    def format(self, obj=None, opts={}):
        if obj is None:
            obj = self.obj
        return self._format(obj, opts)
    
    def _format(self, obj, opts):
        '''Format the object according to our named format.
        
        If possible, all contained fields will be formatted under the same format, 
        and will be passed the same options.
        '''
       
        # Note We want to pass a 'quote' option to all our fields (this will be
        # interpreted by the field formatter itself). If not allready set, we
        # need to create a copy of opts, in order not to break our caller's 
        # formatting (sharing the same opts dict).
        
        if not opts.get('quote'):
            opts = copy.copy(opts)
            opts['quote'] = True

        name = self.requested_name
        argv = list()
        for k, field in obj.iter_fields():
            v = field.get(obj)
            if v is None:
                continue
            # Find a proper formatter for field
            fo = formatter_for_field(field, name)
            if fo:
                fo_opts = opts
                fo_conf = formatters.config_for_field(field, name)
                if fo_conf and 'extra-opts' in fo_conf:
                    fo_opts = copy.copy(fo_opts)
                    fo_opts.update(fo_conf.get('extra-opts'))
                v = fo.format(v, opts=fo_opts)
            else:
                v = format(v)
            argv.append((k, v))
        
        args = ' '.join(map(lambda t: '%s=%s' % t, argv))
        s = '<%s %s>' % (type(obj).__name__, args)
        
        return s   

def formatter_for_object(obj, name='default'):
    '''Get a proper formatter for an object instance.
    '''

    assert name in formatters.supported_formats

    formatter = adapter_registry.queryMultiAdapter(
        [obj], IFormatter, 'format:%s' %(name))
    if formatter:
        formatter.requested_name = name
    
    return formatter

