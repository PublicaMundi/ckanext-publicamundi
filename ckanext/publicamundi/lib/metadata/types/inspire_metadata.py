import re
import json
import uuid
import datetime
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary
from lxml import etree

# Fixme: Replace with native parser
from owslib.iso import MD_Metadata

from ckan.plugins.toolkit import toolkit
from ckan.lib.base import model

from ckanext.publicamundi import reference_data
from ckanext.publicamundi.lib import vocabularies
from ckanext.publicamundi.lib import languages
from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata import IInspireMetadata
from ckanext.publicamundi.lib.metadata import xml_serializers
from ckanext.publicamundi.lib.metadata.xml_serializers import object_xml_serialize_adapter

from . import Metadata, deduce, dataset_type
from ._common import *
from .thesaurus import Thesaurus, ThesaurusTerms

_ = toolkit._
strptime = datetime.datetime.strptime

class KeywordsFactory(object):
    
    __slots__ = ('_name',)

    def __init__(self, thesaurus_name='keywords-gemet-inspire-themes'):
        self._name = thesaurus_name
    
    def __call__(self):
        keywords = {}
        keywords[self._name] = ThesaurusTerms(
            terms=[], thesaurus=Thesaurus.lookup(self._name))
        return keywords

class TemporalExtentFactory(object):
    
    def __call__(self):
        return [TemporalExtent()]

class SpatialResolutionFactory(object):
    
    def __call__(self):
        return [SpatialResolution()]

class ConformityFactory(object):
    
    def __call__(self):
        return [Conformity(title=None, degree=None)]

@dataset_type('inspire')
@object_null_adapter()
class InspireMetadata(Metadata):
    
    zope.interface.implements(IInspireMetadata)

    ## Factories for fields ##

    contact = list
    datestamp = None
    languagecode = None
    
    title = None
    identifier = None
    abstract = None
    locator = list
    resource_language = list
    
    topic_category = list

    keywords = KeywordsFactory()
    free_keywords = list

    bounding_box = list

    temporal_extent = TemporalExtentFactory()

    creation_date = None
    publication_date = None
    revision_date = None
    lineage = None
    
    spatial_resolution = SpatialResolutionFactory()
    reference_system = ReferenceSystem

    conformity = list 
    
    access_constraints = list
    limitations = list
    
    responsible_party = list

    ## Deduce methods ## 
    
    @deduce('id')
    def _deduce_id(self):
        # This is meaningfull only for imported/harvested datasets
        identifier = None
        try:
            identifier = uuid.UUID(self.identifier)
        except:
            pass
        else:
            identifier = str(identifier)
        return identifier
    
    @deduce('notes')
    def _deduce_notes(self):
        return self.abstract
    
    @deduce('tags')
    def _deduce_tags(self):
        tags = []
        for kw in self.free_keywords:
            tags.append(dict(name=kw.value, display_name=kw.value))
        for thes_name, thes_terms in self.keywords.items():
            for term in thes_terms.iter_terms():
                tags.append(dict(name=term.value, display_name=term.title))
        return tags if len(tags) else None

    @deduce('spatial')
    def _deduce_spatial(self):
        if not self.bounding_box:
            return None
        bbox = self.bounding_box[0]    
        wblng, eblng, sblat, nblat = bbox.wblng, bbox.eblng, bbox.sblat, bbox.nblat
        bbox_as_geojson = { 
            'type': 'Polygon', 
            'coordinates': [[
                [wblng, sblat], [wblng, nblat],
                [eblng, nblat], [eblng, sblat],
                [wblng, sblat],
            ]]
        }
        return json.dumps(bbox_as_geojson)
    
    @deduce('license_id')
    def _deduce_license(self):
        result = None
        if not self.access_constraints:
            return result
        license_options = model.Package.get_license_options()
        # Try an exact match to the license title
        try:
            iy = [y[0] for y in license_options].index(self.access_constraints[0])
        except ValueError:
            result = u'CC-BY-3.0'
        else:
            result = license_options[iy][1]
        return result
    
    @deduce("language")
    def _deduce_language(self):
        # Convert from ISO 639-2 to an ISO 639-1 language code
        if self.languagecode:
            return languages.get_by_code(self.languagecode).get('alpha2')
        return None

# XML serialization

@object_xml_serialize_adapter(IInspireMetadata)
class InspireMetadataXmlSerializer(xml_serializers.BaseObjectSerializer):

    def to_xsd(self, wrap_into_schema=False, type_prefix='', annotate=False):
        '''Return the XSD document as an etree Element.
        '''

        # Note We do not support providing parts of it 
        assert wrap_into_schema

        xsd_file = reference_data.get_path('xsd/isotc211.org-2005/gmd/metadataEntity.xsd')

        xsd = None
        with open(xsd_file, 'r') as fp:
            xsd = etree.parse(fp)
        return xsd.getroot()

    def dumps(self, o=None):
        '''Dump object (instance of InspireMetadata) o as an INSPIRE-complant XML 
        document.
        '''

        import ckan.plugins as p

        if o is None:
            o = self.obj

        s = p.toolkit.render('package/inspire_iso.xml', extra_vars={ 'data': o })
        # Convert: render() always returns unicode
        return s.encode('utf-8') 

    def to_xml(self, o=None, nsmap=None):
        '''Build and return an etree Element to serialize an object (instance of
        InspireMetadata) o.

        Here, in contrast to what base XML serializer does, we build the etree by
        parsing the XML string (generated by a Jinja2 template).
        '''

        s = self.dumps(o)
        e = etree.fromstring(s)
        return e

    def from_xml(self, e):
        '''Build and return an InspireMetadata object from a (serialized) etree Element e.
        '''

        def to_date(s):
            return strptime(s, '%Y-%m-%d').date() if isinstance(s, str) else None

        def to_responsible_party(alist):
            result = []
            for it in alist:
                result.append(ResponsibleParty(
                    organization = unicode(it.organization),
                    email = unicode(it.email),
                    role = it.role))
            return result

        # Parse object

        md = MD_Metadata(e)

        datestamp = to_date(md.datestamp)
        id_list = md.identification.uricode

        url_list = []
        if md.distribution:
            for it in md.distribution.online:
                url_list.append(it.url)

        topic_list = []
        for topic in md.identification.topiccategory:
            topic_list.append(topic)
        
        free_keywords = []
        keywords = {}
        for it in md.identification.keywords:
            thes_title = it['thesaurus']['title']
            # Lookup and instantiate a named thesaurus
            thes = None
            if thes_title:
                try:
                    thes_title, thes_version = thes_title.split(',')
                except:
                    thes_version = None
                else:
                    thes_version = re.sub(r'^[ ]*version[ ]+(\d\.\d)$', r'\1', thes_version)
                # Note thes_version can be used to enforce a specific thesaurus version
                try:
                    thes = Thesaurus.lookup(title=thes_title, for_keywords=True)
                except ValueError:
                    thes = None
            # Treat present keywords depending on if they belong to a thesaurus
            if thes:
                # Treat as thesaurus terms; discard unknown terms
                terms = []
                for keyword in it['keywords']:
                    term = thes.vocabulary.by_value.get(keyword)
                    if not term:
                        term = thes.vocabulary.by_token.get(keyword)
                    if term:
                        terms.append(term.value)
                keywords[thes.name] = ThesaurusTerms(thesaurus=thes, terms=terms)
            else:
                # Treat as free keywords (not really a thesaurus)
                vocab_date = to_date(it['thesaurus']['date'])
                vocab_datetype = it['thesaurus']['datetype']
                if thes_title:
                    thes_title = unicode(thes_title)
                for keyword in it['keywords']:
                    free_keywords.append(FreeKeyword(
                        value = keyword,
                        reference_date = vocab_date,
                        date_type = vocab_datetype,
                        originating_vocabulary = thes_title))

        temporal_extent = []
        if md.identification.temporalextent_start or md.identification.temporalextent_end:
            temporal_extent = [TemporalExtent(
                start = to_date(md.identification.temporalextent_start),
                end = to_date(md.identification.temporalextent_end))]

        bbox = []
        if md.identification.extent:
            if md.identification.extent.boundingBox:
                bbox = [GeographicBoundingBox(
                    nblat = float(md.identification.extent.boundingBox.maxy),
                    sblat = float(md.identification.extent.boundingBox.miny),
                    eblng = float(md.identification.extent.boundingBox.maxx),
                    wblng = float(md.identification.extent.boundingBox.minx))]

        creation_date = None
        publication_date = None
        revision_date = None

        for it in md.identification.date:
            if it.type == 'creation':
                creation_date = to_date(it.date)
            elif it.type == 'publication':
                publication_date = to_date(it.date)
            elif it.type == 'revision':
                revision_date = to_date(it.date)

        spatial_list = []

        if len(md.identification.distance) != len(md.identification.uom):
            raise Exception(_('Found unequal list lengths distance,uom (%s, %s)' % (
                    md.identification.distance,md.identification.uom)))
        else:
                for i in range(0,len(md.identification.distance)):
                    spatial_list.append(SpatialResolution(
                        distance = int(md.identification.distance[i]),
                        uom = unicode(md.identification.uom[i])))

                for i in range(0, len(md.identification.denominators)):
                    spatial_list.append(SpatialResolution(
                        denominator = int(md.identification.denominators[i])))
        conf_list = []
        invalid_degree = False
        #if md.referencesystem.codeSpace:
        #    code_space = md.referenceSystem.codeSpace
        reference_system = None
        if md.referencesystem:
            code = md.referencesystem.code
            reference_systems = vocabularies.by_name('reference-systems').get('vocabulary')
            if code in reference_systems:
                # Check whether the URI is provided 
                reference_system = ReferenceSystem(code = code)
            else:
                # Check whether just the EPSG code suffix is provided
                code_full = 'http://www.opengis.net/def/crs/EPSG/0/{code}'.format(code=code)
                if code_full in reference_systems:
                    reference_system = ReferenceSystem(code = code_full)
                else:
                    raise Exception(_('Reference system not recognizable'))

            if md.referencesystem.codeSpace:
                reference_system.code_space = md.referencesystem.codeSpace
            if md.referencesystem.version:
                reference_system.version = md.referencesystem.version

        if len(md.dataquality.conformancedate) != len(md.dataquality.conformancedatetype):
            # Date list is unequal to datetype list, this means wrong XML so exception is thrown
            raise Exception(_('Found unequal list lengths: conformance date, conformancedatetype'))
        if len(md.dataquality.conformancedegree) != len(md.dataquality.conformancedate):
            # Degree list is unequal to date/datetype lists, so we are unable to conclude
            # to which conformity item each degree value corresponds, so all are set to 
            # not-evaluated (Todo: MD_Metadata bug #63)
            invalid_degree = True

        if md.dataquality.conformancedate:
        #and len(md.dataquality.conformancedate) == len(md.dataquality.degree):
            for i in range(0,len(md.dataquality.conformancedate)):

                date = to_date(md.dataquality.conformancedate[i])

                date_type = md.dataquality.conformancedatetype[i]
                # TODO md.dataquality.conformancedatetype returns empty
                if invalid_degree:
                    degree = 'not-evaluated'
                else:
                    try:
                        if md.dataquality.conformancedegree[i] == 'true':
                            degree = 'conformant'
                        elif md.dataquality.conformancedegree[i] == 'false':
                            degree = 'not-conformant'
                    except:
                        degree = "not-evaluated"
                title = unicode(md.dataquality.conformancetitle[i])
                if title != 'None': 
                    conf_list.append(Conformity(title=title, date=date, date_type=date_type, degree=degree))

                # TODO: is title required fields? If so the following is unnecessary
                else:
                    conf_list.append(Conformity(date=date, date_type=date_type, degree=degree))

        limit_list = []
        for it in md.identification.uselimitation:
                limit_list.append(unicode(it))
        constr_list = []
        for it in md.identification.otherconstraints:
                constr_list.append(unicode(it))

        obj = InspireMetadata()

        obj.contact = to_responsible_party(md.contact)
        obj.datestamp = datestamp
        obj.languagecode = md.languagecode
        obj.title = unicode(md.identification.title)
        obj.abstract = unicode(md.identification.abstract)
        obj.identifier = id_list[0]
        obj.locator = url_list
        #obj.resource_language = md.identification.resourcelanguage
        obj.topic_category = topic_list
        obj.keywords = keywords
        obj.free_keywords = free_keywords
        obj.bounding_box = bbox
        obj.temporal_extent = temporal_extent
        obj.creation_date = creation_date
        obj.publication_date = publication_date
        obj.revision_date = revision_date
        obj.lineage = unicode(md.dataquality.lineage)
        obj.spatial_resolution = spatial_list
        obj.reference_system = reference_system
        obj.conformity = conf_list
        obj.access_constraints = limit_list
        obj.limitations = constr_list
        obj.responsible_party = to_responsible_party(md.identification.contact)

        return obj

