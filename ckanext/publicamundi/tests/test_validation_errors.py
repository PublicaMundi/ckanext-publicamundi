import zope.interface
import zope.schema
import copy
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

# Fixture x1: schema validation errors

x1 = Foo(
    baz = u'Bazzz',
    title = u'Ababoua Ababoua',
    tags = [ u'alpha', u'beta', u'gamma', 42, 'aaa'],
    url = 'example.com',
    temporal_extent = TemporalExtent(start=datetime.date(2014, 5, 27), end='bad date'),
    contact_info = ContactInfo(email='booooo'),
    contacts = { 'personal': ci11, 'office': ci12, 'boo': ContactInfo(email=u'foo@example.com') },
    geometry = [[poly1, poly2,], ['boo', 'far']],
    thematic_category = 'environmental',
    created = datetime.datetime(2014, 5, 27, 18, 0, 0),
    wakeup_time = datetime.time(20, 0, 0),
    rating = -100,
    grade = 50.5,
)

# Fixture x2: invariant errors

x2 = Foo(
    baz = u'Bazzz',
    title = u'Ababoua Ababoua',
    tags = [ u'alpha', u'beta', u'gamma', u'alpha'], # duplicate 
    url = 'http://example.com',
    contact_info = ci21,
    contacts = { 'personal': ci21, 'office': ci21 }, # empty
    geometry = [],
    thematic_category = 'environment',
    temporal_extent = TemporalExtent( # bad interval
        start = datetime.date(2014, 5, 27),
        end = datetime.date(2014, 5, 20)),
    created = datetime.datetime(2014, 5, 27, 18, 0, 0),
    wakeup_time = datetime.time(20, 0, 0),
    rating = 0,
    grade = 0.0,
)

# Fixture x3: valid (fix errors on x2)

x3 = copy.deepcopy(x2)
x3.tags = [u'hello-world', u'goodbye']
x3.contacts = {
    'personal':  ContactInfo(email=u'nobody@example.com'),
    'office': ContactInfo(address=PostalAddress(address=u'Nowhere-Land', postalcode=u'12345'))
}
x3.contact_info = ContactInfo(email=u'nomad@somewhere.com')
x3.temporal_extent.end = datetime.date(2014, 5, 28)

## Tests ##

def test_x1():
    '''Find schema validation errors'''
    errs1 = x1.validate()
    errs1_dict = x1.dictize_errors(errs1)
    assert errs1_dict
    expected_keys = set([
        'tags', 'url', 'contact_info', 'contacts', 'temporal_extent', 'geometry', 'thematic_category',
        'rating', 'grade'])
    assert expected_keys.issubset(set(errs1_dict.keys())) 
    print json.dumps(errs1_dict, indent=4)

def test_x2():
    '''Find invariant errors'''
    errs2 = x2.validate()
    errs2_dict = x2.dictize_errors(errs2)
    assert errs2_dict
    expected_keys = set(['__after', 'contact_info', 'temporal_extent', 'contacts'])
    assert expected_keys.issubset(set(errs2_dict.keys())) 
    print json.dumps(errs2_dict, indent=4)

def test_x3():
    '''Verify a valid object'''
    errs3 = x3.validate()
    assert not errs3

## Main ##

if __name__ == '__main__':
    test_x1();
    test_x2();
    test_x3();

