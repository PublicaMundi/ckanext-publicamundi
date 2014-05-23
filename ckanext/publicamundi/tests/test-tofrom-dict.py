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
}

x1 = ContactInfo().from_dict(d1)

errs = x1.get_validation_errors()

d1a = x1.to_dict(flat=True)

