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
        'personal':  ContactInfo(email=u'nobody@example.com'),
        'office': ContactInfo(address=PostalAddress(address=u'Nowhere-Land', postalcode=u'12345'))
    },
    geometry = [[ poly1 ]],
    reviewed = False,
    created = datetime.datetime(2014, 06, 11),
    wakeup_time = datetime.time(8, 0, 0),
    notes = u'Hello World',
    thematic_category = None,
    temporal_extent = dt1,
)

# Schema validation errors, name, email not list
rp1 = ResponsibleParty("Non unicode name","non unicode email","Author")

# Schema validation errors, empty fields
rp2 = ResponsibleParty(u"org",[u""],u"")

# Schema validation errors, email not correct
rp3 = ResponsibleParty(u"unicode name",["unicodenon@email"],u"author")

# No schema errors
rp_correct = ResponsibleParty(u"org",[u"correct@email.com"],"author")

# '''Find schema validation errors: originating_vocabulary,date_type'''
fkw1 = FreeKeyword(u"val",None,datetime.date(1000,1,1),"creationn")

# '''Find schema validation invariant error - not all fields set'''
fkw2 = FreeKeyword(u"val",None,datetime.date.today(),'creation')

# '''Validate correct schema'''
fkw_correct = FreeKeyword(u"val",u"original",datetime.date.today(),'creation')

# '''Find schema validation errors: all not float'''
gbb1 = GeographicBoundingBox(50,50,40,30)

#'''Find schema validation errors - nblat, wblng greater than max allowed'''
gbb2 = GeographicBoundingBox(-1235.0,0.0,123.123,1235.0)

# '''Validate correct schema'''
gbb_correct = GeographicBoundingBox(-50.0,-20.12,0.0,15.0)

# '''Find schema validation errors: start not date'''
te1 = TemporalExtent(2015,datetime.date.today())

# '''Find schema invariant error - start date greater than end date'''
te2 = TemporalExtent(datetime.date(2015,01,01),datetime.date.today())

# '''Validate correct schema'''
te_correct = TemporalExtent(datetime.date.today(), datetime.date(2015,01,01))

# '''Find schema validation errors date, creation, degree'''
cnf1 = Conformity(u"lala", 2015,"creationn", "confofrmant")
# '''Validate correct schema'''
cnf_correct = Conformity(u"lala",datetime.date.today(),"creation","conformant")

# '''Find schema validation error - distance not int '''
sr1 = SpatialResolution(5.0,u"lala")

# '''Find schema invariant error - not all values set'''
sr2 = SpatialResolution(5, None)

# '''Validate correct schema - no values set'''
sr3 = SpatialResolution(None,None)

#'''Validate correct schema'''
sr_correct = SpatialResolution(5, u"lala")

