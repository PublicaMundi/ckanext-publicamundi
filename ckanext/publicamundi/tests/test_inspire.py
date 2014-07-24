import zope.interface
import zope.schema
import copy
import json
import datetime

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.base import *
from ckanext.publicamundi.tests.helpers import assert_faulty_keys
from ckanext.publicamundi.tests.fixtures import *

#
# INSPIRE fixtures
#

thesaurus_gemet_concepts = Thesaurus(
    title = u'GEMET Concepts',
    name = 'keywords-gemet-concepts',
    reference_date = datetime.date(2014, 1, 1),
    date_type = 'creation'
)

thesaurus_gemet_themes = Thesaurus(
    title = u'GEMET Themes',
    name = 'keywords-gemet-themes',
    reference_date = datetime.date(2014, 5, 1),
    date_type = 'creation'
)

thesaurus_gemet_inspire_data_themes = Thesaurus(
    title = u'GEMET INSPIRE Data Themes',
    name = 'keywords-gemet-inspire-data-themes',
    reference_date = datetime.date(2014, 6, 1),
    date_type = 'publication'
)

# Missing required title, abstract
insp11 = InspireMetadata(
        contact = [
            ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
        datestamp = datetime.date.today(),
        languagecode = "el",
        identifier = [u"12314213123"],
        locator = ["http://www.google.com"],
        resource_language = ["el"],
        topic_category = ["biota"],
        keywords = [
            ThesaurusTerms(
                terms=["atmosphere"],
                thesaurus=thesaurus_gemet_concepts
            ),            
            ThesaurusTerms(
                terms=["land-cover", "land-use"],
                thesaurus=thesaurus_gemet_inspire_data_themes,
            ),
        ],
        bounding_box = [
            GeographicBoundingBox(nblat=0.0, sblat=0.0, eblng=0.0, wblng=0.0)],
        temporal_extent = [
            TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2013,1,1))],
        creation_date = datetime.date(2012,1,1),
        publication_date = datetime.date(2013,1,1),
        revision_date = datetime.date(2014,1,1),
        lineage = u"lineaage",
        denominator = [0,1,2],
        spatial_resolution = [SpatialResolution(distance=0, uom=u"meters")],
        conformity = [
            Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
        access_constraints = [u"lalala1", u"lalala2"],
        limitations = [u"limit1", u"limit2"],
        responsible_party = [
            ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), 
            ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])

# Missing required topic_category, responsible_party
insp12 = InspireMetadata(
    contact = [
        ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com", "http://publicamundi.eu"],
    resource_language = ["el"],
    keywords = [
        ThesaurusTerms(
            terms=["atmosphere"],
            thesaurus=thesaurus_gemet_concepts
        ),
        ThesaurusTerms(
            terms=["land-cover", "land-use"],
            thesaurus=thesaurus_gemet_inspire_data_themes,
        ),
    ],
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [
        TemporalExtent(start = datetime.date(2012,1,1), end = datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2,3],
    spatial_resolution = [SpatialResolution(distance=5, uom = u"meters")],
    conformity = [
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"])

# Creation, publication, revision wrong date ranges & temporal extent start, end (invariant)
insp2 = InspireMetadata(
    contact = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com"],
    resource_language = ["el"],
    topic_category = ["biota"],
    keywords = [
        ThesaurusTerms(
            terms=["buildings"],
            thesaurus=thesaurus_gemet_inspire_data_themes,
        ),
        ThesaurusTerms(
            terms=["atmosphere"],
            thesaurus=thesaurus_gemet_concepts)
    ],
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, eblng=0.0, wblng=0.0)],
    temporal_extent = [
        TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2013,1,1))],
    creation_date = datetime.date(2014,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2012,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2],
    spatial_resolution = [
        SpatialResolution(distance=0, uom=u"meters")],
    conformity = [
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")])

# Min_length of contact, locator smaller than one 
insp3 = InspireMetadata(
    contact = [],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = [],
    resource_language = ["el"],
    topic_category = ["biota"],
    keywords = [
        ThesaurusTerms(
            terms=["buildings"],
            thesaurus=thesaurus_gemet_inspire_data_themes,
        ),
        ThesaurusTerms(
            terms=["atmosphere"],
            thesaurus=thesaurus_gemet_concepts)
    ],
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [
        TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2,3],
    spatial_resolution = [
        SpatialResolution(distance=5, uom=u"meters")],
    conformity = [
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), 
        ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])

# Temporal-Extent start field (required field in ITemporalExtent) missing
insp4 = InspireMetadata(
    contact = [
        ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com", "http://publicamundi.eu"],
    resource_language = ["el"],
    topic_category = ["biota"],
    keywords = [
        ThesaurusTerms(
            terms=["buildings"],
            thesaurus=thesaurus_gemet_inspire_data_themes,
        ),
        ThesaurusTerms(
            terms=["atmosphere"],
            thesaurus=thesaurus_gemet_concepts
        ),
    ],
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [
        TemporalExtent(end=datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2,3],
    spatial_resolution = [
        SpatialResolution(distance=5, uom=u"meters")],
    conformity = [
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1" ,u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), 
        ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])

# Temporal-Extent (not required field) missing 
insp5 = copy.deepcopy(insp4)
insp5.temporal_extent = None

# Temporal-Extent wrong date range
insp6 = copy.deepcopy(insp4)
insp6.temporal_extent = [
    TemporalExtent(start=datetime.date(2013,1,1), end=datetime.date(2012,1,1))],

# Keywords include unexpected terms
insp7 = copy.deepcopy(insp4)
insp7.temporal_extent = None
insp7.keywords = [
    ThesaurusTerms(
        terms=["buildings", "addresses"],
        thesaurus=thesaurus_gemet_inspire_data_themes,
    ),
    ThesaurusTerms(
        terms=["analysis", "foo"], # Term "foo" does not exist
        thesaurus=thesaurus_gemet_concepts
    ),
]

# Everything should be ok 
insp8 = InspireMetadata(
    contact = [
        ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://publicamundi.eu", "http://www.google.com", "http://www.ipsyp.gr", "http://www.example.com"],
    resource_language = ["el"],
    topic_category = ["biota"],
    keywords = [
        ThesaurusTerms(
            terms=["air", "agriculture", "climate"],
            thesaurus=thesaurus_gemet_themes
        ),    
        ThesaurusTerms(
            terms=["buildings", "addresses"],
            thesaurus=thesaurus_gemet_inspire_data_themes,
        ),
    ],
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
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), 
        ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")]
)

def test_insp11():
    ''' Missing required title, abstract'''
    assert_faulty_keys(insp11, 
        expected_keys=set(['title', 'abstract']))

def test_insp12():
    '''Missing required topic_category, responsible_party'''
    assert_faulty_keys(insp12,
        expected_keys=set(['topic_category', 'responsible_party']))

def test_insp2():
    ''' Creation, publication, revision date ranges not valid'''
    assert_faulty_keys(insp2,
        expected_keys = set(['__after']), 
        expected_invariants = ["later than publication date", "later than last revision date"]
    )

def test_insp3():
    ''' Min_length of contact, locator smaller than min_length'''
    assert_faulty_keys(insp3,
        expected_keys=set(['contact', 'locator']))

def test_insp4():
    '''Temporal-Extent start field (required field in ITemporalExtent) missing'''
    assert_faulty_keys(insp4,
        expected_keys=set(['temporal_extent']))

def test_insp5():
    '''Temporal-Extent (not required field) missing'''
    assert_faulty_keys(insp5)

def test_insp6():
    '''Temporal-Extent wrong date range'''
    assert_faulty_keys(insp6,
        expected_keys=set(['temporal_extent']), expected_invariants=["later than end date"])

def test_insp7():
    '''Unexpected keywords (not found in vocabularies)'''
    assert_faulty_keys(insp7,
        expected_keys=set(['keywords']))

def test_insp8():
    assert_faulty_keys(insp8)

if __name__ == '__main__':
    #test_insp11()
    #test_insp12()
    #test_insp2()
    #test_insp3()
    #test_insp4()
    #test_insp5()
    #test_insp6()
    test_insp7()
    #test_insp8()


