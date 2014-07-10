import datetime
import copy

from ckanext.publicamundi.lib.metadata.types import *

## Objects ##

pt1 = Point(x=0.76, y=0.23)

contact1 = ContactInfo(
    email = u'somebody@example.com', 
    address = PostalAddress(address=u'Nowhere Land', postalcode=u'12321'))

poly1 = Polygon(name = u'Poly1', points=[
    Point(x=0.6, y=0.5), Point(x=0.7, y=0.1),
    Point(x=1.6, y=0.2), Point(x=0.6, y=0.5),])

poly2 = Polygon(name = u'Poly2', points=[
    Point(x=7.9, y=0.8), Point(x=1.3, y=0.2),
    Point(x=1.6, y=0.2), Point(x=7.9, y=0.8),])

dt1 = TemporalExtent(
    start = datetime.date(2014, 5, 27),
    end = datetime.date(2014, 5, 29))

foo1 = Foo(
    baz = u'Bazzz',
    title = u'Ababoua Ababoua',
    tags = [ u'alpha', u'beta', u'gamma'],
    url = 'http://example.com',
    contact_info = ContactInfo(email=u'nomad@somewhere.com'),
    contacts = {
        'personal':  ContactInfo(email=u'nobody@example.com', address=PostalAddress(address=u'North Pole', postalcode=u'54321')),
        'office': ContactInfo(address=PostalAddress(address=u'South Pole', postalcode=u'12345')),
    },
    geometry = [[ poly1, poly2 ]],
    reviewed = False,
    created = datetime.datetime(2014, 06, 11),
    wakeup_time = datetime.time(8, 0, 0),
    notes = u'Hello World',
    thematic_category = None,
    temporal_extent = dt1,
    rating = 0,
    grade = 13.7,
    password = u'secret',
)

