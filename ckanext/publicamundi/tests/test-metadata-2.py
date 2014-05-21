import zope.interface
import zope.schema
import ckanext.publicamundi.lib.metadata as pm_metadata
import logging

X = pm_metadata.InspireMetadata

S = X.get_schema()

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

if __name__  == '__main__':
    res = flatten_schema(S)
    for k in res:
        print k, '->', res[k]

