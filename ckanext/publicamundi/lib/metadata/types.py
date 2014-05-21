import zope.interface
import zope.schema
import logging

import ckanext.publicamundi.lib

from ckanext.publicamundi.lib.metadata.schema import IBaseMetadata
from ckanext.publicamundi.lib.metadata.schema import ICkanMetadata, IInspireMetadata

def flatten_schema(S):
    assert S.extends(zope.interface.Interface)
    res = {}
    fields = zope.schema.getFields(S)
    for k,F in fields.items():
        res1 = flatten_field(F)
        for k1,f1 in res1.items():
            res[(k,)+k1] = f1
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
            for k,f in res1.items():
                res[(i,)+k] = f
    else:
        res = { (): F }
    return res

class BaseMetadata(object):
    
    _schema = None

    @classmethod
    def _find_schema(cls):
        for iface in zope.interface.implementedBy(cls):
            if iface.extends(IBaseMetadata):
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
        return flatten_schema(S)

class CkanMetadata(BaseMetadata):
    zope.interface.implements(ICkanMetadata)

    def __init__(self):
        pass

class InspireMetadata(BaseMetadata):
    zope.interface.implements(IInspireMetadata)

    def __init__(self):
        pass

