import zope.interface
import ckan.plugins as p
from ckanext.publicamundi.lib.metadata.types.common import *
from ckanext.publicamundi.lib.metadata.schemata.inspire import *
from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.types import object_null_adapter

@object_null_adapter(IThesaurus)
class Thesaurus(Object):
    zope.interface.implements(IThesaurus)

    title = None
    reference_date = None
    date_type = None
    value = None
    terms = list


@object_null_adapter(IInspireMetadata)
class InspireMetadata(Object):
    zope.interface.implements(IInspireMetadata)

    contact = list
    datestamp = None
    languagecode = None
    title = None
    identifier = list
    abstract = None
    locator = list
    resource_language = list
    topic_category = list
    keywords = list
    bounding_box = list
    temporal_extent = list
    creation_date = None
    publication_date = None
    revision_date = None
    lineage = None
    denominator = list
    spatial_resolution = list
    conformity = list
    access_constraints = list
    limitation = list
    responsible_party = list

    '''
    @classmethod
    def from_xml(cls,infile):
        def to_date(str):
            return datetime.datetime.strptime(str,'%Y-%m-%d').date()
        def to_resp_party(alist):
            result = []
            for it in alist:
                result.append(ResponsibleParty(unicode(it.organization),[unicode(it.email)],it.role))
            return result

        md = MD_Metadata(etree.parse(infile))
        datestamp = to_date(md.datestamp)
        id_list = []
        for it in md.identification.uricode:
            id_list.append(unicode(it))

        url_list = []
        for it in md.distribution.online:
            url_list.append(it.url)

        keywords_list = []
        for it in md.identification.keywords:
            kw = {}
            kw['name'] = it['thesaurus']['title']
            kw['value'] = it['thesaurus']['title']
            kw['terms'] = it['keywords']
            kw['date'] = it['thesaurus']['date']
            kw['datetype'] = it['thesaurus']['datetype']
            keywords_list.append(kw)

        temporal_extent = [TemporalExtent(to_date(md.identification.temporalextent_start),to_date(md.identification.temporalextent_end))]
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

        if not creation_date:
            raise Exception('creation date not present','')
        elif not publication_date:
            raise Exception('publication date not present','')
        elif not revision_date:
            raise Exception('revision date not present','')

        denom_list = []
        for it in md.identification.denominators:
            try:
                parsed_int = int(it)
                denom_list.append(parsed_int)
            except:
                print 'Cannot parse denominator'

        #denom_list = md.identification.denominators

        spatial_list = []

        if len(md.identification.distance) != len(md.identification.uom):
            raise Exception('unequal list lengths distance,uom','%s %s' % (md.identification.distance,md.identification.uom))
        else:
            for i in range(0,len(md.identification.distance)):
                spatial_list.append(SpatialResolution(md.identification.distance[i],md.identification.uom[i]))

        conf_list = []

        if len(md.dataquality.conformancedate) != len(md.dataquality.conformancedatetype):
            raise Exception('unequal list lengths conformance date,conformancedatetype','!')
        else:
            for i in range(0,len(md.dataquality.conformancedate)):
                if md.dataquality.conformancetitle[i]:
                    conf_list.append(Conformity(unicode(md.dataquality.conformancetitle[i]),to_date(md.dataquality.conformancedate[i]),md.dataquality.conformancedatetype[i],md.dataquality.conformancedegree[i]))
                else:
                    conf_list.append(Conformance(None,to_datemd.dataquality.conformancedate[i]),md.dataquality.conformancedatetype[i],md.dataquality.conformancedegree[i])
        limit_list = []
        for it in md.identification.uselimitation:
                limit_list.append(unicode(it))
        constr_list = []
        for it in md.identification.otherconstraints:
                constr_list.append(unicode(it))

        return InspireMetadata(to_resp_party(md.contact), datestamp,  md.languagecode, unicode(md.identification.title),id_list , unicode(md.identification.abstract), url_list, md.identification.resourcelanguage, md.identification.topiccategory, keywords_list, [GeographicBoundingBox(float(md.identification.extent.boundingBox.maxy),float(md.identification.extent.boundingBox.miny),float(md.identification.extent.boundingBox.maxx),float(md.identification.extent.boundingBox.minx))], temporal_extent, creation_date, publication_date, revision_date, unicode(md.dataquality.lineage), denom_list, spatial_list, conf_list, limit_list, constr_list, to_resp_party(md.identification.contact))
    '''

@classmethod
def to_xml(cls,imd,outfile):

    # Save custom record to a valid ISO XML file
    #env = Environment(loader=FileSystemLoader('.'))
    #env.globals.update(zip=zip)
    #template = env.get_template('mdmetadata_iso.xml')
    #iso_xml = template.render(md=md)
    iso_xml = p.toolkit.render('package/inspire_iso.xml',extra_vars={'data':imd})
    xml_file = outfile
    xml_file = open(outfile, "w")
    xml_file.write(iso_xml)
    xml_file.close()
