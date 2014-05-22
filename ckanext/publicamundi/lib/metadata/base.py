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
    
    # Fixme: Check invariants for nested objects!

    def get_validation_errors(self):
        S = self.get_schema()
        return zope.schema.getValidationErrors(S, self)
    
    def validate_invariants(self):
        S = self.get_schema()
        return S.validateInvariants(self)
        
    def validate(self):
        S = self.get_schema()
        # Invoke field-level validators
        for k,F in zope.schema.getFields(S).items():
            F.validate(F.get(self))
        # Check object-level invariants
        S.validateInvariants(self)
        return

    def to_dict(self, flatten=False):
        if flatten:
            return self.flattened()
        else:
            return self.dictized()

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
    def _find_schema(cls):
        for iface in zope.interface.implementedBy(cls):
            if iface.extends(IBaseObject):
                return iface
        return None
    
    @classmethod
    def get_schema(cls):
        if not cls._schema:
            cls._schema = cls._find_schema()
        return cls._schema

    @classmethod
    def get_fields(cls):
        S = cls.get_schema()
        return zope.schema.getFields(S)
    
    @classmethod
    def get_flattened_fields(cls):
        S = cls.get_schema()
        return flattened_schema(S)

    ## Helpers
    
    def dictized(self):
        S = self.get_schema()
        res = {}
        fields = zope.schema.getFields(S)
        for k,F in fields.items():
            res[k] = self.dictized_field(F)
        return res
        
    def dictized_field(self, F):
        assert isinstance(F, zope.schema.Field)
        f = F.get(self)
        res = None
        if isinstance(F, zope.schema.Object):
            if isinstance(f, BaseObject):
                res = f.dictized()
            else:
                res = f
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple): 
            res = []
            for i,y in enumerate(f):
                if isinstance(y, BaseObject):
                    res.append(y.dictized())
                else:
                    res.append(y)
        else:
            res = f
        return res

    def flattened(self):
        S = self.get_schema()
        res = {}
        fields = zope.schema.getFields(S)
        for k,F in fields.items():
            res1 = self.flattened_field(F)
            for k1,f1 in res1.items():
                res[(k,)+k1] = f1
        return res

    def flattened_field(self, F):
        assert isinstance(F, zope.schema.Field)
        f = F.get(self)
        res = None
        if isinstance(F, zope.schema.Object):
            if isinstance(f, BaseObject):
                res = f.flattened()
            else:
                res = { (): f }
        elif isinstance(F, zope.schema.List) or isinstance(F, zope.schema.Tuple):
            res = {}
            for i,y in enumerate(f):
                # Note we do not support nested lists
                if isinstance(y, BaseObject):
                    for yk,yf in y.flattened().items():
                        res[(i,)+yk] = yf
                else:
                    res[(i,)] = y 
        else:
            res = { (): f }
        return res

