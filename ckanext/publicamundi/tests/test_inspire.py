import zope.interface
import zope.schema
import copy
import json
import datetime
from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.types.inspire import *
from ckanext.publicamundi.lib.metadata.base import *
from ckanext.publicamundi.tests.helpers import assert_faulty_keys
from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.tests.fixtures import *


#
# Inspire fixtures
#

# Missing required title, abstract(not lists)
insp1 = InspireMetadata(
        contact = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
        datestamp = datetime.date.today(),
        languagecode = "el",
        identifier = [u"12314213123"],
        locator = ["http://www.google.com"],
        resource_language = ["el"],
        topic_category = ["biota"],
        keywords = [Thesaurus(terms=["addresses"],
            name="inspire_data_themes",
            title=u"Inspire Data Themes",
            reference_date=datetime.date(2000,1,1),
            date_type='creation')],
        bounding_box = [GeographicBoundingBox(nblat=0.0, sblat=0.0, eblng=0.0, wblng=0.0)],
        temporal_extent = [TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2013,1,1))],
        creation_date = datetime.date(2012,1,1),
        publication_date = datetime.date(2013,1,1),
        revision_date = datetime.date(2014,1,1),
        lineage = u"lineaage",
        denominator = [0,1,2],
        spatial_resolution = [SpatialResolution(distance=0, uom=u"meters")],
        conformity = [Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
        access_constraints = [u"lalala1", u"lalala2"],
        limitations = [u"limit1", u"limit2"],
        responsible_party = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])

# Missing required topic_category, responsible_party(lists)
insp1_5 = InspireMetadata(contact = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com", "http://publicamundi.eu"],
    resource_language = ["el"],
    keywords = [Thesaurus(terms=["addresses"],
        name="inspire_data_themes",
        title=u"Inspire Data Themes",
        reference_date=datetime.date(2000,1,1),
        date_type='creation')],
    bounding_box = [GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [TemporalExtent(start = datetime.date(2012,1,1), end = datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2,3],
    spatial_resolution = [SpatialResolution(distance=5, uom = u"meters")],
    conformity = [Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"])

# Creation, publication, revision date not in order & temporal extent start,end (invariant)
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
    keywords = [Thesaurus(terms = ["addresses"],
            name = "inspire_data_themes",
            title = u"Inspire Data Themes",
            reference_date = datetime.date(2000,1,1),
            date_type = 'creation')],
    bounding_box = [GeographicBoundingBox(nblat=0.0, sblat=0.0, eblng=0.0, wblng=0.0)],
    temporal_extent = [TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2013,1,1))],
    creation_date = datetime.date(2014,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2012,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2],
    spatial_resolution = [SpatialResolution(distance=0, uom=u"meters")],
    conformity = [Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")])

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
    keywords = [Thesaurus(terms=["addresses"],
        name="inspire_data_themes",
        title=u"Inspire Data Themes",
        reference_date=datetime.date(2000,1,1),
        date_type='creation')],
    bounding_box = [GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2,3],
    spatial_resolution = [SpatialResolution(distance=5, uom=u"meters")],
    conformity = [Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])

# Temporal extent start field (required field in ITemporalExtent) missing
insp4 = InspireMetadata(contact = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com", "http://publicamundi.eu"],
    resource_language = ["el"],
    topic_category = ["biota"],
    keywords = [Thesaurus(terms=["addresses"],
        name="inspire_data_themes",
        title=u"Inspire Data Themes",
        reference_date=datetime.date(2000,1,1),
        date_type='creation')],
    bounding_box = [GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [TemporalExtent(end=datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2,3],
    spatial_resolution = [SpatialResolution(distance=5, uom=u"meters")],
    conformity = [Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1" ,u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])

# Temporal Extent (not required field) missing 
insp5 = InspireMetadata(contact = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com", "http://publicamundi.eu"],
    resource_language = ["el"],
    topic_category = ["biota"],
    keywords = [Thesaurus(terms=["addresses"],
        name="inspire_data_themes",
        title=u"Inspire Data Themes",
        reference_date=datetime.date(2000,1,1),
        date_type='creation')],
    bounding_box = [GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [0,1,2,3],
    spatial_resolution = [SpatialResolution(distance=5, uom=u"meters")],
    conformity = [Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])

# Inspire Wrong temporal extent date order (invariant in subclass)
insp6 = InspireMetadata(contact = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://publicamundi.eu", "http://www.google.com", "http://www.ipsyp.gr", "http://www.lala.gr"],
    resource_language = ["el"],
    topic_category = ["biota"],
    keywords = [Thesaurus(terms=["addresses"],
        name="inspire_data_themes",
        title=u"Inspire Data Themes",
        reference_date=datetime.date(2000,1,1),
        date_type='creation'),
        Thesaurus(terms=["accident"],
        name="gemet_concepts",
        title=u"Gemet Concepts",
        reference_date=datetime.date(2000,1,1),
        date_type='creation'),
        Thesaurus(terms=["time_(chronology)"],
        name="gemet_groups",
        title=u"Gemet Groups",
        reference_date=datetime.date(2000,1,1),
        date_type='creation')],
    bounding_box = [GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [TemporalExtent(start=datetime.date(2013,1,1), end=datetime.date(2012,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [],
    spatial_resolution = [SpatialResolution(distance=5, uom=u"meters")],
    conformity = [Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])

# Inspire correct schema 
insp7 = InspireMetadata(contact = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact")],
    datestamp = datetime.date.today(),
    languagecode = "el",
    title = u"Title",
    identifier = [u"12314213123"],
    abstract = u"abstracttttttt",
    locator = ["http://publicamundi.eu", "http://www.google.com", "http://www.ipsyp.gr", "http://www.lala.gr"],
    resource_language = ["el"],
    topic_category = ["biota"],
    keywords = [Thesaurus(terms=["addresses"],
        name="inspire_data_themes",
        title=u"Inspire Data Themes",
        reference_date=datetime.date(2000,1,1),
        date_type='creation'),
        Thesaurus(terms=["accident"],
        name="gemet_concepts",
        title=u"Gemet Concepts",
        reference_date=datetime.date(2000,1,1),
        date_type='creation'),
        Thesaurus(terms=["time_(chronology)"],
        name="gemet_groups",
        title=u"Gemet Groups",
        reference_date=datetime.date(2000,1,1),
        date_type='creation')],
    bounding_box = [GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    denominator = [],
    spatial_resolution = [SpatialResolution(distance=5, uom=u"meters")],
    conformity = [Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [ResponsibleParty(organization=u"Org", email=[u"email@asd.gr"], role="pointofcontact"), ResponsibleParty(organization=u"Org2", email=[u"email2@asd.gr"], role="pointofcontact")])


def test_insp1():
    ''' Missing required title, abstract (not lists) '''
    assert_faulty_keys(field=insp1, expected_keys=set(['title', 'abstract']))

def test_insp1_5():
    '''Missing required topic_category, responsible_party(lists)'''
    assert_faulty_keys(field=insp1_5, expected_keys=set(['topic_category', 'responsible_party']))

def test_insp2():
    ''' Creation, publication, revision date not in order'''
    assert_faulty_keys(field=insp2, expected_keys=set(['__after']), expected_invariants=["later than publication date","later than last revision date"])

def test_insp3():
    ''' Min_length of contact, locator smaller than min_length'''
    assert_faulty_keys(field=insp3, expected_keys=set(['contact', 'locator']))

def test_insp4():
    '''Temporal extent start field (required field in ITemporalExtent) missing'''
    assert_faulty_keys(field=insp4, expected_keys=set(['temporal_extent']))

def test_insp5():
    '''Temporal Extent (not required field) missing'''
    assert_faulty_keys(field=insp5)

def test_insp6():
    '''Wrong temporal extent date order (invariant in subclass)'''
    assert_faulty_keys(field=insp6, expected_keys=set(['temporal_extent']), expected_invariants=["later than end date"])

def test_insp7():
    '''Validate correct inspire schema'''
    assert_faulty_keys(field=insp7)

if __name__ == '__main__':
    test_insp3()
