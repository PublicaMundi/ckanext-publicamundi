import zope.interface
import zope.schema
from zope.interface.verify import verifyObject

import json

from ckanext.publicamundi.lib.metadata.types import *

def print_as_dict(o):
    assert isinstance(o, BaseObject)

    d1 = o.to_dict(flat=False)
    print json.dumps(d1, indent=4)
    
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

    ci1 = ContactInfo(
        address = PostalAddress(
            address = u'Acacia Avenue',
            postalcode = u'11362'),
        email = u'foo@example.com',
    )
    ci2 = ContactInfo(
        email = u'boo@example.com',
    )
    ci3 = ContactInfo(
        email = u'baz@example.com',
    )
    ci4 = ContactInfo()
    
    geom1 = [
        [
            Polygon(
                points=[
                    Point(x=0.6, y=0.5),
                    Point(x=0.7, y=0.1),
                    Point(x=1.6, y=0.2),
                    Point(x=0.6, y=0.5),
                ],
                name = u'A1'
            ),            
            Polygon(
                points=[
                    Point(x=1.2, y=0.4),
                    Point(x=1.7, y=0.1),
                    Point(x=1.6, y=0.2),
                    Point(x=1.2, y=0.4),
                ],
                name = u'A2'
            ),
        ],[
            Polygon(
                points=[
                    Point(x=5.1, y=4.5),
                    Point(x=4.7, y=3.8),
                    Point(x=4.6, y=3.2),
                    Point(x=4.6, y=4.5),
                    Point(x=5.1, y=4.5),
                ],
                name = u'B1'
            ), 
        ],
    ]

    x1 = InspireMetadata(
        foo = 'bar',
        baz = u'Bazzz',
        title = u'Ababoua Ababoua', 
        tags = [ u'alpha', u'beta', u'gamma', ], 
        url = 'http://example.com',
        contact_info = ci2,
        contacts = { 'personal': ci1, 'office': ci2 },
        geometry = geom1,
        thematic_category = 'environment',
    )

    validate_fields(x1)

    errors = x1.get_validation_errors()    
    if not errors:
        print_as_dict(x1)
    

    # Test {to/from}_dict

    d1 = x1.to_dict()
    x2 = InspireMetadata().from_dict(d1)

    s1 = json.dumps(d1)
    s2 = json.dumps(x2.to_dict())
    assert s1 == s2
    



