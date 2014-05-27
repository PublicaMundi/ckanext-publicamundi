import zope.interface
import zope.schema
import json

from ckanext.publicamundi.lib.metadata.types import *

d1 = {
    'address': {
        'address': u'Acacia Avenue',
        'postalcode': u'11362',
    },
    'email': u'foo@example.com',
    'foo': u'i am ignored',
}

x1 = ContactInfo().from_dict(d1)

errs = x1.validate()

d1a = x1.to_dict(flat=True)

s1  = x1.to_json()
s1a = x1.to_json(flat=True, indent=4)


