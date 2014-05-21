import zope.interface
import zope.schema
import logging

import ckanext.publicamundi.lib

from ckanext.publicamundi.lib.metadata.schema import *

def flattened_schema(S):
    assert S.extends(zope.interface.Interface)
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
        # Todo
        pass
    
    def flattened(self):
        S = self.get_schema()
        # Todo
        pass

    def flattened_field(self, F):
        assert isinstance(F, zope.schema.Field)
        f = F.get(self)
        res = None
        if isinstance(f, BaseObject):
            res = f.flattened()
        elif isinstance(f, list) or isinstance(f, tuple):
            res = {}
            for i,y in enumerate(f):
                # Note we do not support nested lists
                if isinstance(y, BaseObject):
                    for yk,yf in y.flattened().items():
                        res[(i,)+yk] = yf
                else:
                    res[(i,)] = y 
                    pass
        else:
            res = { (): f }
        return res

class BaseMetadata(BaseObject):
    pass

class ContactInfo(BaseObject):
    zope.interface.implements(IContactInfo)
    
    email = None
    address = None
    postalcode = None

    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)

class CkanMetadata(BaseMetadata):
    zope.interface.implements(ICkanMetadata)

    title = None
    
    def __init__(self, **kwargs):
        BaseMetadata.__init__(self, **kwargs)

class InspireMetadata(BaseMetadata):
    zope.interface.implements(IInspireMetadata)
    
    title = None
    url = None
    thematic_category = None
    tags = list
    baz = None
    contact_info = ContactInfo

    def __init__(self, **kwargs):
        BaseMetadata.__init__(self, **kwargs)

