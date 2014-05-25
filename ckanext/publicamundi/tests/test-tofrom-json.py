import zope.interface
import zope.schema
import json
import logging

from ckanext.publicamundi.lib.metadata.types import *

poly1 = Polygon(name = u'P1', points=[
    Point(x=0.6, y=0.5), Point(x=0.7, y=0.1), 
    Point(x=1.6, y=0.2), Point(x=0.6, y=0.5),
]) 

x1 = InspireMetadata(
    baz = u'Bazzz',
    title = u'Ababoua Ababoua', 
    tags = [ u'alpha', u'beta', u'gamma'], 
    url = 'http://example.com',
    contact_info = ContactInfo(email=u'nomad@somewhere.com'),
    contacts = { 
        'personal':  ContactInfo(email=u'nobody@example.com'), 
        'office': ContactInfo(address=PostalAddress(address=u'Nowhere-Land', postalcode=u'12345'))   
    },
    geometry = [[ poly1 ]],
    thematic_category = 'environment',
)

errs = x1.validate()
assert not errs

s1d = x1.to_json(flat=False, indent=4)
s1f = x1.to_json(flat=True, indent=4)

x2 = InspireMetadata()
try:
    x2.from_json(s1d, is_flat=False)
    s2d = x2.to_json(flat=False, indent=4)
    s2f = x2.to_json(flat=True, indent=4)
    if s1d != s2d: 
        logging.error('s1d != s2d: Method from_json(is_flat=F) does not work as expected')
    if s1f != s2f:
        logging.error('s1d != s2f: Method from_json(is_flat=F) does not work as expected')
except Exception as ex:
    logging.error('Cannot serialize/deserialize from (nested) JSON')
    raise ex

x3 = InspireMetadata()
try: 
    x3.from_json(s1f, is_flat=True)
    s3d = x3.to_json(flat=False, indent=4)
    s3f = x3.to_json(flat=True, indent=4)
    if s1d != s3d: 
        logging.error('s1d != s3d: Method from_json(is_flat=T) does not work as expected')
    if s1f != s3f:
        logging.error('s1d != s3f: Method from_json(is_flat=T) does not work as expected')
except Exception as ex:
    logging.error('Cannot serialize/deserialize from (flattened) JSON')
    raise ex


