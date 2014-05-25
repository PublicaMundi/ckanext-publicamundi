import threading
import logging
import zope.interface
import zope.interface.verify
import zope.schema

import ckanext.publicamundi.lib.dictization as dictization
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.schema import IBaseObject

_logger = logging.getLogger(__name__)

_cache = threading.local()

def flatten_schema(S):
    assert S.extends(IBaseObject)
    res = {}
    fields = zope.schema.getFields(S)
    for k,F in fields.items():
        res1 = flatten_field(F)
        for k1,F1 in res1.items():
            res[(k,)+k1] = F1
    return res

def flatten_field(F):
    assert isinstance(F, zope.schema.Field)
    res = None
    if isinstance(F, zope.schema.Object):
        res = flatten_schema(F.schema)
    elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
        res = {}
        res1 = flatten_field(F.value_type)
        for i in range(0, F.max_length):
            for k1,F1 in res1.items():
                res[(i,)+k1] = F1
    elif isinstance(F, zope.schema.Dict):
        assert isinstance(F.key_type, zope.schema.Choice), 'Only zope.schema.Choice supported for key_type'
        res = {}
        res1 = flatten_field(F.value_type)
        for v in F.key_type.vocabulary:
            for k1,F1 in res1.items():
                res[(v.token,)+k1] = F1
    else:
        res = { (): F }
    return res

class BaseObject(object):
    zope.interface.implements(IBaseObject)
    
    default_factories = {
        zope.schema.TextLine: None,
        zope.schema.Text: None,
        zope.schema.BytesLine: None,
        zope.schema.Bytes: None,
        zope.schema.Int: None,
        zope.schema.Float: None,
        zope.schema.Bool: None,
        zope.schema.Datetime: None,
        zope.schema.List: list,
        zope.schema.Tuple: list,
        zope.schema.Dict: dict,
    }

    ## interface IBaseObject

    @classmethod
    def schema(cls):
        return cls.get_schema()

    def validate(self):
        return self._validate()

    def to_dict(self, flat=False):
        if flat:
            return self.flatten()
        else:
            return self.dictize()

    def from_dict(self, d):
        assert isinstance(d, dict)
        is_flat = isinstance(d.iterkeys().next(), tuple)
        if is_flat:
            d = dictization.unflatten(d)
        self._construct(d)
        # provide method chaining
        return self
        
    ## Constructor based on keyword args 
    
    def __init__(self, **kwargs):
        cls = type(self)
        S = cls.get_schema()
        for k,F in zope.schema.getFields(S).items():
            v = kwargs.get(k)
            if not v:
                factory = cls.get_field_factory(k, F)
                v = factory() if factory else F.default
            setattr(self, k, v)
    
    ## Provide a string representation

    def _repr(self):
        cls = type(self)
        typename = cls.__name__ #"%s:%s" %(cls.__module__, cls.__name__)
        s = '<' + typename
        for k,F in self.get_fields().items():
            f = F.get(self)
            if f:
                s += ' %s=%s' %(k, repr(f))
        s += '>'
        return s

    __repr__ = _repr

    ## Introspective class methods

    @classmethod
    def lookup_schema(cls):
        S = None
        for iface in zope.interface.implementedBy(cls):
            if iface.extends(IBaseObject):
                S = iface
                break
        return S
    
    @classmethod
    def get_schema(cls):
        S = None
        if not hasattr(_cache, 'schema'):
            _cache.schema = {}
        try:
            S = _cache.schema[cls]
        except KeyError:
            S  = cls.lookup_schema()
            _cache.schema[cls] = S
        return S

    @classmethod
    def get_fields(cls):
        S = cls.get_schema()
        return zope.schema.getFields(S)
    
    @classmethod
    def get_flattened_fields(cls):
        S = cls.get_schema()
        return flatten_schema(S)
 
    @classmethod
    def get_field_factory(cls, k, F=None):
        assert not k or isinstance(k, basestring)
        assert not F or isinstance(F, zope.schema.Field)
        assert k or F, 'At least one of k(key), F(Field) should be specified' 
        factory = None
        # Check if a factory is defined explicitly as a class attribute
        if k and hasattr(cls, k):
            factory = getattr(cls, k)
            return factory
        # Find a sensible factory for this field 
        if not F:
            S = cls.get_schema()
            F = S.get(k)
            if not F:
                raise ValueError('Cannot find field %s for schema %s' %(k,S))
        if isinstance(F, zope.schema.Object):
            factory = adapter_registry.lookup([], F.schema) 
        else:
            factory = F.defaultFactory or cls.default_factories.get(type(F))
        return factory

    ## Validation helpers
    
    def _validate(self):
        '''Return a list <errors> structured as: 
          
          errors ::= [ (k, ef), ... ]      
          ef ::= [ ex1, ex2, ...] 
          ex ::= Invalid(arg0, arg1, ...)
          arg0 ::= errors
          arg0 ::= <literal-value>

        Notation:
          ef : field-errors 
          ex : exception (derived from Invalid)

        '''
        errors = self._validate_schema() 
        if errors:
            # Do not continue checking invariants
            return errors
        else:
            return self._validate_invariants()

    def _validate_schema(self):
        '''Returns <errors>'''
        S = self.get_schema()
        errors = []
        for k,F in zope.schema.getFields(S).items():
            f = F.get(self)
            ef = self._validate_schema_for_field(f, F)
            if ef:
                errors.append((k, ef))
        return errors
    
    def _validate_schema_for_field(self, f, F):
        '''Returns <ef>, i.e. an array of field-specific exceptions'''
        ef = []
        # Check if empty
        if f is None:
            # Check if required
            try:
                F.validate(f)
            except zope.interface.Invalid as ex:
                ef.append(ex)
            return ef
        # If here, we have an non-empty field
        if isinstance(F, zope.schema.Object):
            # Check interface is provided by instance f 
            try:
                zope.interface.verify.verifyObject(F.schema, f)
            except zope.interface.Invalid as ex:
                ef.append(ex)
            # If provides, proceed to schema validation
            if not ef:
                errors = f._validate_schema()
                if errors:
                    ef.append(zope.interface.Invalid(errors))
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
            # Check type
            if not (isinstance(f, list) or isinstance(f, tuple)):
                try:
                    F.validate(f)
                except zope.interface.Invalid as ex:
                    ef.append(ex)
            # If type is ok, proceed to schema validation
            if not ef:
                errors = self._validate_schema_for_field_items(enumerate(f), F)
                if errors:
                    ef.append(zope.interface.Invalid(errors))
        elif isinstance(F, zope.schema.Dict):
            # Check type
            if not isinstance(f, dict):
                try:
                    F.validate(f)
                except zope.interface.Invalid as ex:
                    ef.append(ex)
            # If type is ok, proceed to schema validation
            if not ef:
                errors = self._validate_schema_for_field_items(f.iteritems(), F)
                if errors:
                    ef.append(zope.interface.Invalid(errors))
        else:
            try:
                F.validate(f)
            except zope.interface.Invalid as ex:
                ef.append(ex)
        return ef

    def _validate_schema_for_field_items(self, items, F):
        '''Returns <errors>'''
        errors = []
        for k,y in items:
            ef = self._validate_schema_for_field(y, F.value_type)
            if ef:
                errors.append((k, ef))
        return errors

    def _validate_invariants(self):
        '''Return <errors>'''
        S = self.get_schema()
        errors = []
        
        # Descend into field invariants
        recurse = False
        try:
            recurse = S.getTaggedValue('recurse-on-invariants')
        except KeyError:
            pass
        if recurse:
            for k,F in zope.schema.getFields(S).items():
                f = F.get(self)
                if not f:
                    continue
                ef = self._validate_invariants_for_field(f, F)
                if ef:
                    errors.append((k, ef))
                
        # Check own invariants
        try:
            S.validateInvariants(self)
        except zope.interface.Invalid as ex:
            errors.append((None, [ex]))
        
        return errors

    def _validate_invariants_for_field(self, f, F):
        '''Returns <ef>, i.e. an array of field-specific exceptions'''
        ef = []

        errors = None
        if isinstance(F, zope.schema.Object):
            errors = f._validate_invariants()
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
            errors = self._validate_invariants_for_field_items(enumerate(f), F)
        elif isinstance(F, zope.schema.Dict):
            errors = self._validate_invariants_for_field_items(f.iteritems(), F)
        
        if errors:
            ef.append(zope.interface.Invalid(errors))
        return ef

    def _validate_invariants_for_field_items(self, items, F):
        '''Returns <errors>'''
        errors = []
        for k,y in items:
            ef = self._validate_invariants_for_field(y, F.value_type)
            if ef:
                errors.append((k, ef))
        return errors
    
    ## Error helpers - Convert to other formats 
    
    def dictize_errors(self, errors):
        return self._dictize_errors(errors)

    INVARIANT_ERROR_KEY = '<invariant>'
    
    def _dictize_errors(self, errors):
        cls = type(self)
        S = cls.get_schema()
        res = dict()
        for k, ef in errors:
            # Pick the 1st exception (is this ok?)
            ex = ef[0]
            if k is None:
                # Found a failed invariant
                if not res.has_key(cls.INVARIANT_ERROR_KEY):
                    res[cls.INVARIANT_ERROR_KEY] = list()
                res[cls.INVARIANT_ERROR_KEY].append(str(ex))
            else:
                # Found a field-specific error
                F = S.get(k)
                if not F:
                    continue
                f = F.get(self)
                res[k] = self._dictize_errors_for_field(ex, f, F)
        return res
    
    def _dictize_errors_for_field(self, ex, f, F):
        assert isinstance(ex, zope.interface.Invalid), 'Validation errors derive from Invalid'
        # Check if we must descend 
        if not (ex.args and isinstance(ex.args[0], list)):
            # Treat this as a literal, stop descending
            return '%s: %s' %(type(ex).__name__, str(ex).strip())    
        
        # If here, we have a valid <errors> list
        errors = ex.args[0]
        if isinstance(F, zope.schema.Object):
            # If supports further dictization, descent into object
            if isinstance(f, BaseObject):
                return f._dictize_errors(errors)
            else:
                return errors
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
            return self._dictize_errors_for_field_collection(errors, f, F)
        elif isinstance(F, zope.schema.Dict):
            return self._dictize_errors_for_field_collection(errors, f, F)
        else:
            return '%s: %s' %(type(ex).__name__, repr(errors))
 
    def _dictize_errors_for_field_collection(self, errors, f, F):
        res = {} 
        for k, ef in errors:
            # Pick the 1st exception
            ex = ef[0]
            # Note that here, k will be either an integer or a string
            res[k] = self._dictize_errors_for_field(ex, f[k], F.value_type) 
        return res
        
    
    def flatten_errors(self, errors):
        error_dict = self._dictize_errors(errors)
        return dictization.flatten(error_dict)

    ## Dictization helpers
    
    def dictize(self):
        return self._dictize()

    def _dictize(self): 
        S = self.get_schema()
        res = {}
        fields = zope.schema.getFields(S)
        for k,F in fields.items():
            f = F.get(self)
            res[k] = self._dictize_field(f, F) if f else None
        return res

    def _dictize_field(self, f, F):
        if isinstance(F, zope.schema.Object):
            return f._dictize()
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
            a = list()
            for i,y in enumerate(f):
                a.append(self._dictize_field(y, F.value_type))
            return a
        elif isinstance(F, zope.schema.Dict):
            d = dict()
            for k,y in f.items():
                d[k] = self._dictize_field(y, F.value_type) 
            return d
        else:
            return f

    def flatten(self):
        return self._flatten()

    def _flatten(self): 
        S = self.get_schema()
        res = {}
        fields = zope.schema.getFields(S)
        for k,F in fields.items():
            f = F.get(self)
            if f:
                res1 = self._flatten_field(f, F)
                for k1,v1 in res1.items():
                    res[(k,)+k1] = v1
        return res

    def _flatten_field(self, f, F):
        if isinstance(F, zope.schema.Object):
            return f._flatten()
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
            return self._flatten_field_items(enumerate(f), F)
        elif isinstance(F, zope.schema.Dict):
            return self._flatten_field_items(f.iteritems(), F)
        else:
            return { (): f }

    def _flatten_field_items(self, items, F):
        d = {}
        for k,y in items:
            res1 = self._flatten_field(y, F.value_type)
            for k1,v1 in res1.items():
                d[(k,)+k1] = v1
        return d
   
    def _construct(self, d):
        cls = type(self)
        S = cls.get_schema()
        for k,F in zope.schema.getFields(S).items():
            v = d.get(k)
            factory = cls.get_field_factory(k, F)
            f = None
            if not v: 
                # No value given, use factory (if exists)
                f = factory() if factory else F.default
            else:
                # Input provided a value on k
                f = self._make_field(v, F, factory)
            setattr(self, k, f)

    def _make_field(self, v, F, factory=None):
        assert isinstance(F, zope.schema.Field)
        # Find a factory (if missing)
        if not factory:
            factory = self.get_field_factory(None, F)
        # Create a new field instance
        if isinstance(F, zope.schema.Object):
            f = factory()
            f._construct(v)
            return f
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
            a = list()
            for i,y in enumerate(v):
                v1 = self._make_field(y, F.value_type)
                a.append(v1)
                pass
            return a
        elif isinstance(F, zope.schema.Dict):
            d = dict()
            for k,y in v.items():
                v1 = self._make_field(y, F.value_type)
                d[k] = v1
            return d
        else:
            return v
       
