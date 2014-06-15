import datetime

from ckanext.publicamundi.lib.metadata.types import *

poly1 = Polygon(name = u'P1', points=[
    Point(x=0.6, y=0.5), Point(x=0.7, y=0.1),
    Point(x=1.6, y=0.2), Point(x=0.6, y=0.5),])

dt1 = TemporalExtent(
    start = datetime.datetime(2014, 5, 27, 1, 30, 0),
    end = datetime.datetime(2014, 5, 29, 1, 30, 0))

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
    temporal_extent = dt1,
)

