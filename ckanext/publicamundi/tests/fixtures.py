import datetime
import copy

from ckanext.publicamundi.lib.metadata.types import *

## Objects ##

pt1 = Point(x=0.76, y=0.23)

poly1 = Polygon(name = u'P1', points=[
    Point(x=0.6, y=0.5), Point(x=0.7, y=0.1),
    Point(x=1.6, y=0.2), Point(x=0.6, y=0.5),])

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
        'office': ContactInfo(email=u'somebody@company.com', address=PostalAddress(address=u'South Pole', postalcode=u'12345')),
    },
    geometry = [[ poly1 ]],
    reviewed = False,
    created = datetime.datetime(2014, 06, 11),
    wakeup_time = datetime.time(8, 0, 0),
    notes = u'Hello World',
    thematic_category = None,
    temporal_extent = dt1,
)

