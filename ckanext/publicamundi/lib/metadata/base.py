import zope.interface
import zope.schema

import ckanext.publicamundi.lib
from ckanext.publicamundi.lib.metadata.schema import IBaseObject

def flattened_schema(S):
    assert S.extends(IBaseObject)
    res = {}
    fields = zope.schema.getFields(S)
    for k,F in fields.items():
        res1 = flattened_field(F)
        for k1,f1 in res1.items():
            res[(k,)+k1] = f1
    return res

def flattened_field(F):
    assert isinstance(F, zope.schema.Field)
    res = None
    if isinstance(F, zope.schema.Object):
        res = flattened_schema(F.schema)
    elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
        res = {}
        res1 = flattened_field(F.value_type)
        for i in range(0, F.max_length):
            for k,f in res1.items():
                res[(i,)+k] = f
    else:
        res = { (): F }
    return res

class BaseObject(object):
    zope.interface.implements(IBaseObject)

    _schema = None
   
    ## interface IBaseObject

    def get_validation_errors(self):
        return self._validate()

    def to_dict(self, flat=False):
        if flat:
            return self.flatten()
        else:
            return self.dictize()

    ## Constructor based on keyword args 
    
    def __init__(self, **kwargs):
        cls = type(self)
        S = cls.get_schema()
        for k in zope.schema.getFieldNames(S):
            v = kwargs.get(k)
            if not v:
                factory = getattr(cls,k)
                if factory:
                    v = factory()
            setattr(self,k,v)

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
        return flattened_schema(S)

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
            self._validate_invariants_for_field_list(f, F)
        elif isinstance(F, zope.schema.Dict):
            self._validate_invariants_for_field_dict(f, F)
                    
    def _validate_invariants_for_field_list(self, f, F):
        errors = []
        for i,y in enumerate(f):
            try:
                self._validate_invariants_for_field(y, F.value_type)       
            except zope.interface.Invalid as ex:
                errors.append((i,ex))
        if errors:
            raise zope.interface.Invalid(errors)
          
    def _validate_invariants_for_field_dict(self, f, F):
        errors = []
        for k,y in f.items():
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
            return self._dictize_field_list(f, F)
        elif isinstance(F, zope.schema.Dict):
            return self._dictize_field_dict(f, F)
        else:
            return f

    def _dictize_field_list(self, f, F):
        a = []
        for i,y in enumerate(f):
            a.append(self._dictize_field(y, F.value_type))
        return a
    
    def _dictize_field_dict(self, f, F):
        d = {}
        for k,y in f.items():
            d[k] = self._dictize_field(y, F.value_type) 
        return d

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
   
