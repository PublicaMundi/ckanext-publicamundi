import zope.interface
import zope.schema
import logging

import ckanext.publicamundi.lib.dictization as dictization
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.schema import IBaseObject

log1 = logging.getLogger(__name__)

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

    # Fixme thread-safety issues?
    _schema = None
    
    default_factories = {
        zope.schema.TextLine: unicode,
        zope.schema.Text: unicode,
        zope.schema.BytesLine: str,
        zope.schema.Bytes: str,
        zope.schema.Int: None,
        zope.schema.Float: None,
        zope.schema.Bool: None,
        zope.schema.Datetime: None,
        zope.schema.List: list,
        zope.schema.Tuple: list,
        zope.schema.Dict: dict,
    }

    ## interface IBaseObject

    def get_validation_errors(self):
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
        return self._construct(d)
        
    ## Constructor based on keyword args 
    
    def __init__(self, **kwargs):
        cls = type(self)
        S = cls.get_schema()
        for k,F in zope.schema.getFields(S).items():
            v = kwargs.get(k)
            if not v:
                factory = cls.get_field_factory(k, F)
                if factory:
                    v = factory()
            setattr(self, k, v)

    ## Introspective class methods

    @classmethod
    def _detect_schema(cls):
        for iface in zope.interface.implementedBy(cls):
            if iface.extends(IBaseObject):
                return iface
        return None
    
    @classmethod
    def get_schema(cls):
        if not cls._schema:
            cls._schema = cls._detect_schema()
        return cls._schema

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
        assert k or F, 'At least one of k,F should be specified' 
        factory = None
        # Check if a factory is defined explicitly as a class attribute
        try:
            if k:
                factory = getattr(cls, k)
        except AttributeError:
            pass
        if factory:
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
        S = self.get_schema()
        errors = zope.schema.getSchemaValidationErrors(S, self)
        if errors:
            return errors
        errors = []
        try:
            self._validate_invariants()
        except zope.interface.Invalid as ex:
            errors.append(ex)
        return errors

    def _validate_invariants(self):
        S = self.get_schema()
        # Validate field invariants
        recurse = False
        try:
            recurse = S.getTaggedValue('recurse-on-invariants')
        except KeyError:
            pass
        if recurse:
            errors = []
            for k,F in zope.schema.getFields(S).items():
                f = F.get(self)
                if not f:
                    continue
                try:
                    self._validate_invariants_for_field(f,F)
                except zope.interface.Invalid as ex:
                    errors.append((k,ex))
            if errors:
                raise zope.interface.Invalid(errors)
                
        # Check own invariants
        try:
            S.validateInvariants(self)
        except zope.interface.Invalid as ex:
            raise zope.interface.Invalid((None,ex))

    def _validate_invariants_for_field(self, f, F):
        if isinstance(F, zope.schema.Object):
            f._validate_invariants()
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
            self._validate_invariants_for_field_items(enumerate(f), F)
        elif isinstance(F, zope.schema.Dict):
            self._validate_invariants_for_field_items(f.iteritems(), F)
                    
    def _validate_invariants_for_field_items(self, items, F):
        errors = []
        for k,y in items:
            try:
                self._validate_invariants_for_field(y, F.value_type)       
            except zope.interface.Invalid as ex:
                errors.append((k,ex))
        if errors:
            raise zope.interface.Invalid(errors)

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
        log1.info('Building an object as %s; schema=%s', cls, S)
        for k,F in zope.schema.getFields(S).items():
            v = d.get(k)
            factory = cls.get_field_factory(k, F)
            f = None
            if not v: 
                # No value, use factory (if exists)
                f = factory() if factory else None
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
       
