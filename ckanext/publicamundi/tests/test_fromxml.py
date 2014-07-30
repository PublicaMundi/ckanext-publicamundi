import zope.interface
import zope.schema
import copy
import json
import datetime

from ckanext.publicamundi.lib.metadata.types.inspire import InspireMetadata, ThesaurusTerms, Thesaurus
from ckanext.publicamundi.lib.metadata.types.common import *
from ckanext.publicamundi.lib.metadata.base import *
from ckanext.publicamundi.tests.helpers import assert_faulty_keys
from ckanext.publicamundi.tests.fixtures import *

infile = "tests/samples/corine_2000.xml"
outfile = "out.xml" 

insp_xml = InspireMetadata()
insp_xml.from_xml(infile)
#print repr(insp_xml)

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
insp8.to_xml(outfile)
print repr(insp8)

def test_xml():
    '''Test from xml'''
    assert_faulty_keys(insp_xml)

    insp8.to_xml(outfile)
if __name__ == '__main__':
    #test_insp11()
    #test_insp12()
    #test_insp2()
    #test_insp3()
    #test_insp4()
    #test_insp5()
    #test_insp6()
    test_xml()
    #test_insp8()


