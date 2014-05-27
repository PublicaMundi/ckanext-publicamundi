import zope.interface
import zope.schema
from zope.interface.verify import verifyObject

import json

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.tests.fixtures import x1

def print_as_dict(o):
    assert isinstance(o, BaseObject)

    d1 = o.to_dict(flat=False)
    print d1 #json.dumps(d1, indent=4)
    
    d2 = o.to_dict(flat=True)
    for k in sorted(d2):
        print k, ':', d2[k]   

def validate_fields(o):
    S = o.get_schema()
    for k,F in zope.schema.getFields(S).items():
        f = F.get(o)
        e = None
        try:
            F.validate(f)
        except zope.interface.Invalid as ex:
            e = ex     

if __name__  == '__main__':

    validate_fields(x1)

    errors = x1.validate()    
    if not errors:
        print_as_dict(x1)

    # Test {to/from}_dict

    d1r = x1.to_dict()
    x2 = InspireMetadata().from_dict(d1r)

    d1f = x1.to_dict(flat=True) 
    x3 = InspireMetadata().from_dict(d1f, is_flat=True)
    

