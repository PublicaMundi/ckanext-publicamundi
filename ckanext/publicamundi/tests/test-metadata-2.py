import zope.interface
import zope.schema
import json

from ckanext.publicamundi.lib.metadata.types import *

def print_as_dict(o):
    assert isinstance(o, BaseObject)

    print json.dumps(o.to_dict(), indent=4)

    for k,v in o.to_dict(flatten=True).items():
        print k, ':', v   

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

    x1 = InspireMetadata(
        foo = 'bar', 
        title = u'Ababoua', 
        tags = [u'alpha', u'beta', u'gamma'], 
        url = 'http://example.com',
        contact_info = ci1,
        contacts = [ci2, ci4],
    )
    
    errors = x1.get_validation_errors()    
    print errors

    if not errors:
        print_as_dict(x1)

