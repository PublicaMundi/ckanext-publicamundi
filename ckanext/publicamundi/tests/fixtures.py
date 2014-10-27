# -*- encoding: utf-8 -*-

import datetime
import copy

from ckanext.publicamundi.lib.metadata.types import *

## Initialize objects ##

pt1 = Point(x=0.76, y=0.23)

contact1 = ContactInfo(
    email = u'nowhere-man@example.com', 
    address = PostalAddress(address=u'Nowhere Land', postalcode=u'12321'))

contact2 = ContactInfo(
    email = u'somebody@example.com', 
    address = PostalAddress(address=u'Ακακίας 22', postalcode=u'54321'))

contact3 = ContactInfo(
    email = u'penguin@example.com', 
    address = PostalAddress(address=u'North Pole', postalcode=u'91911'))

poly1 = Polygon(name = u'Poly1', points=[
    Point(x=0.6, y=0.5), Point(x=0.7, y=0.1),
    Point(x=1.6, y=0.2), Point(x=0.6, y=0.5),])

poly2 = Polygon(name = u'Poly2', points=[
    Point(x=7.9, y=0.8), Point(x=1.3, y=0.2),
    Point(x=1.6, y=0.2), Point(x=7.9, y=0.8),])

poly3 = Polygon(name = u'Poly3', points=[
    Point(x=3.6, y=1.8), Point(x=1.5, y=5.2),
    Point(x=1.2, y=7.2), Point(x=3.6, y=1.8),])

dt1 = TemporalExtent(
    start = datetime.date(2014, 5, 27),
    end = datetime.date(2014, 5, 29))

dt2 = TemporalExtent(
    start = datetime.date(1999, 5, 1),
    end = datetime.date.today())

freekeyword1 = FreeKeyword(
    value = u"atmosphere",
    originating_vocabulary = u"Foo-1",
    reference_date = datetime.date.today(),
    date_type = 'creation')

party1 = ResponsibleParty(
    organization = u"Acme Org", 
    email = u"someone@acme.org", 
    role = "pointofcontact")

bbox1 = GeographicBoundingBox(nblat=-50.0, sblat=-20.12, wblng=15.0, eblng=1.0)

textent1 = TemporalExtent(start=datetime.date.today(), end=datetime.date(2015,01,01))

conformity1 = Conformity(
    title = u"lala",
    date = datetime.date.today(), 
    date_type = "creation", 
    degree = "conformant")

spatialres1 = SpatialResolution(distance=5, uom=u"lala")

# Foo

foo1 = Foo(
    baz = u'Bazzz',
    title = u'Αβαβούα',
    tags = [ u'alpha', u'beta', u'gamma'],
    url = 'http://example.com/res/1',
    contact_info = ContactInfo(email=u'nomad@somewhere.com', address=None),
    contacts = {
        'personal': ContactInfo(
            publish=False,
            email=u'nobody@example.com', 
            address=PostalAddress(address=u'North Pole', postalcode=u'54321')),
        'office': ContactInfo(
            publish=True,
            email=None, 
            address=PostalAddress(address=u'South Pole', postalcode=u'12345')),
    },
    geometry = [[ poly1, poly2 ]],
    reviewed = False,
    created = datetime.datetime(2014, 06, 11),
    wakeup_time = datetime.time(8, 0, 0),
    notes = u'Hello World',
    thematic_category = 'economy',
    temporal_extent = dt1,
    rating = 0,
    grade = 13.7,
    password = u'secret',
)

foo2 = Foo(
    baz = u'Baobab',
    title = u'Αβαβούα',
    tags = [ u'alpha', u'beta', u'gamma',],
    url = 'ftp://example.com/res/2',
    contact_info = ContactInfo(
        email=u'nomad@somewhere.com', 
        address=PostalAddress(address=u'Sahara', postalcode=u'12329')),
    geometry = [[ poly1 ]],
    reviewed = True,
    created = datetime.datetime(2014, 6, 11),
    wakeup_time = datetime.time(8, 30, 0),
    thematic_category = 'health',
    temporal_extent = None,
    rating = 3,
    grade = -2.79,
    password = u'another-secret',
)

foo3 = copy.deepcopy(foo1)
foo3.rating = None
foo3.grade = None

foo4 = copy.deepcopy(foo1)
foo4.geometry = None

foo5 = copy.deepcopy(foo1)
foo5.contacts = None

foo6 = copy.deepcopy(foo1)
foo6.contacts['personal'] = None

foo7 = copy.deepcopy(foo1)
foo7.tags = None

foo8 = copy.deepcopy(foo1)
foo8.contacts.pop('personal')

# Thesaurus

thesaurus_gemet_concepts = Thesaurus(
    title = u'GEMET Concepts',
    name = 'keywords-gemet-concepts',
    reference_date = datetime.date(2014, 1, 1),
    version = '1.0',
    date_type = 'creation'
)

thesaurus_gemet_themes = Thesaurus.make('keywords-gemet-themes')

thesaurus_gemet_inspire_data_themes = Thesaurus.make('keywords-gemet-inspire-themes')

# Baz 

baz1 = Baz(
    url = 'http://baz.example.com',
    contacts = [contact1, contact2, contact3],
    keywords = ThesaurusTerms(
        terms = ["energy", "agriculture", "climate", "human-health"],
        thesaurus = thesaurus_gemet_themes),
    bbox = bbox1,
)

baz2 = copy.deepcopy(baz1)
baz2.keywords = None #ThesaurusTerms(thesaurus=Thesaurus(name='keywords-gemet-inspire-themes'))
baz2.bbox = None

# INSPIRE metadata

inspire1 = InspireMetadata(
    contact = [party1],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = "http://acme.example.com/datasets/91b54070-5adb-11e4-8ed6-0800200c9a66",
    abstract = u"This is an abstract description",
    locator = [
        "http://publicamundi.eu",
        "http://www.ipsyp.gr",
        "http://www.example.com"
    ],
    resource_language = ["el"],
    topic_category = ["biota", "farming", "economy"],
    keywords = {
        'keywords-gemet-themes': ThesaurusTerms(
            terms=["air", "agriculture", "climate"],
            thesaurus=thesaurus_gemet_themes
        ),
        'keywords-gemet-inspire-themes': ThesaurusTerms(
            terms=["buildings", "addresses"],
            thesaurus=thesaurus_gemet_inspire_data_themes,
        ),
    },
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [
        TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2012,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [],
    spatial_resolution = [
        SpatialResolution(distance=5, uom=u"meters")],
    conformity = [
        Conformity(
            title = u"specifications blabla", 
            date = datetime.date.today(), 
            date_type = "creation", 
            degree = "conformant")
    ],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(
            organization=u"Acme Org", email=u"a@acme.example.com", role="originator"), 
        ResponsibleParty(
            organization=u"Coyote Org", email=u"b@coyote.example.com", role="pointofcontact")]
)

inspire2 = copy.deepcopy(inspire1)
inspire2.keywords = None

