import zope.interface
import zope.schema
import json
import datetime

from ckanext.publicamundi.lib.metadata.types import *

ci11 = ContactInfo(
    address = PostalAddress(address = 'Acacia Avenue 22', postalcode = u'11362'),
    email = u'foo@example.com')
ci12 = ContactInfo(
    address = PostalAddress(address = u'Rue De La Loi', postalcode = u'11555-000'),
    email = u'baz@example.com')

ci21 = ContactInfo() # both fields empty (violates invariant)
ci22 = ContactInfo(
    address = PostalAddress(address = u'Acacia Avenue 22', postalcode = u'11362'),
    email = u'foo@example.com')

poly1 = Polygon(name = u'P1', points=[
    Point(x=0.6, y=0.5), Point(x=0.7, y=0.1),
    Point(x=1.6, y=0.2), Point(x=0.6, y=0.5),
]) 
poly2 = Polygon(name = u'P2', points=[
    Point(x=1.6, y=0.5), Point(x=4.0, y=1.5),
    Point(x=1.2, y=0.1), Point(x=2.8, y=1.2),
    Point(x=1.6, y=0.5),
]) 
poly3 = Polygon(name = u'P3', points=[
    Point(x=1.9, y=1.5), Point(x=0.3, y=0.5),
    Point(x=0.7, y=3.5), Point(x=1.1, y=0.6),
    Point(x=1.9, y=1.5),
]) 

# Test #1: schema validation errors

x1 = InspireMetadata(
    baz = u'Bazzz',
    title = u'Ababoua Ababoua', 
    tags = [ u'alpha', u'beta', u'gamma', 42, 'aaa'], 
    url = 'example.com',
    temporal_extent = TemporalExtent(start=datetime.datetime(2014, 5, 27), end='bad date'),
    contact_info = ContactInfo(email='booooo'),
    contacts = { 'personal': ci11, 'office': ci12 },
    geometry = [[poly1, poly2,], ['boo', 'far']],
    thematic_category = 'environmental',
)

errs1 = x1.validate()

errs1_dict = x1.dictize_errors(errs1)

print json.dumps(errs1_dict, indent=4)

# Test #2: invariant errors

x2 = InspireMetadata(
    baz = u'Bazzz',
    title = u'Ababoua Ababoua', 
    tags = [ u'alpha', u'beta', u'gamma', u'alpha'], # duplicate 
    url = 'http://example.com',
    contact_info = ci21,
    contacts = { 'personal': ci21, 'office': ci21 }, # empty
    geometry = [],
    thematic_category = 'environment',
    temporal_extent = TemporalExtent( # bad interval
        start = datetime.datetime(2014, 5, 27), 
        end = datetime.datetime(2014, 5, 20)),
)

errs2 = x2.validate()

errs2_dict = x2.dictize_errors(errs2)

print json.dumps(errs2_dict, indent=4)

# Test #3: Fix errors and expect success

x2.tags = [u'hello-world', u'goodbye']
x2.contacts = { 
    'personal':  ContactInfo(email=u'nobody@example.com'), 
    'office': ContactInfo(address=PostalAddress(address=u'Nowhere-Land', postalcode=u'12345'))
}
x2.contact_info = ContactInfo(email=u'nomad@somewhere.com')
x2.temporal_extent.end = datetime.datetime(2014, 5, 28)

errs2 = x2.validate()
assert not errs2


