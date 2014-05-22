import zope.interface
import zope.schema
import json

from ckanext.publicamundi.lib.metadata.types import *

def print_as_dict(o):
    assert isinstance(o, BaseObject)

    print json.dumps(o.to_dict(), indent=4)

    for k,v in o.to_dict(flatten=True).items():
        print k, ':', v   

def validate_fields(o, S):
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

        ]
    ]

    x1 = InspireMetadata(
        foo = 'bar', 
        title = u'Ababoua', 
        tags = [u'alpha', u'beta', u'alpha'], 
        url = 'http://example.com',
        contact_info = ci2,
        contacts = [ci1, ci2],
        geometry = geom1,
    )
 
    X = x1.get_schema()
    F = X.get('contacts')

    #validate_fields(x1, X)

    errors = x1.get_validation_errors()    
    print errors

    #if not errors:
    #    print_as_dict(x1)

