import zope.interface
from schema import *
from owslib.iso import *
from jinja2 import Environment, FileSystemLoader
from typedecl_common import *

class InspireMetadata(object):
    zope.interface.implements(IInspireMetadata)
    
    def __init__(self,contact,datestamp,languagecode,title,identifier,abstract,locator,resource_language,topic_category,keywords, bounding_box,temporal_extent,creation_date,publication_date,revision_date,lineage,denominator,spatial_resolution,conformity,access_constraints,limitations,responsible_party):
        self.contact = contact
        self.datestamp = datestamp
        self.languagecode = languagecode
        self.title = title
        self.identifier = identifier
        self.abstract = abstract
        self.locator = locator
        self.resource_language = resource_language
        self.topic_category = topic_category
        self.keywords = keywords
        self.bounding_box = bounding_box
        self.temporal_extent = temporal_extent
        self.creation_date = creation_date
        self.publication_date = publication_date
        self.revision_date = revision_date
        self.lineage = lineage
        self.denominator = denominator
        self.spatial_resolution = spatial_resolution
        self.conformity = conformity
        self.access_constraints = access_constraints
        self.limitations = limitations
        self.responsible_party = responsible_party
    
    def print_fields(self):
        print 'Contact(organization, email,role):'
        for k in self.contact:
            print '(%s , %s, %s) ' % (k.organization,k.email, k.role)
        print 'Date: %s ' % (self.datestamp)
        print 'Language: %s ' % (self.languagecode)
        print 'Title: %s ' % (self.title)
        print 'Id: %s ' % (self.identifier)
        print 'Abstract: %s ' % (self.abstract)
        print 'Locator: %s ' % (self.locator)
        print 'Resource language: %s ' % (self.resource_language)
        print 'Topic category: %s ' % (self.topic_category)
        print 'Keywords: %s ' % (self.keywords)
        for k in self.bounding_box:
            print '(%d , %d, %d, %d) ' % (k.nblat,k.sblat, k.eblng,k.wblng)
        for k in self.temporal_extent:
            print '(%s, %s) ' % (k.start,k.end)
        print 'Creation date: %s ' % (self.creation_date)
        print 'Publication date: %s ' % (self.publication_date)
        print 'Revision date: %s ' % (self.revision_date)
        print 'Lineage: %s ' % (self.lineage)
        print 'Denominator: %s' %(self.denominator)
        for k in self.spatial_resolution:
            print '(%s, %s) ' % (k.distance, k.uom)
        for k in self.conformity:
            print '(%s , %s, %s, %s) ' % (k.title,k.date, k.date_type,k.degree)
        print 'Access constraints: %s ' % (self.access_constraints)
        print 'Limitations: %s ' % (self.limitations)
        for k in self.responsible_party:
            print '(%s , %s, %s) ' % (k.organization,k.email, k.role) 
    
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


    @classmethod
    def to_xml(cls,imd,outfile):
        md = MD_Metadata()

        md.identification = MD_DataIdentification()
        md.dataquality = DQ_DataQuality()
        md.distribution = MD_Distribution()
        md.identification.extent = EX_Extent()
        md.identification.extent.boundingBox = EX_GeographicBoundingBox()

        for it in imd.contact:
            val = CI_ResponsibleParty()
            val.organization = it.organization
            val.email = it.email[0]
            val.role = it.role
            md.contact.append(val)

        md.datestamp = imd.datestamp
        md.languagecode = imd.languagecode
        md.identification.title = imd.title
        md.identification.abstract = imd.abstract
        md.identification.identtype = 'dataset'
        
        for it in imd.locator:
            val = CI_OnlineResource()
            val.url = it
            md.distribution.online.append(val)

        md.identifier = imd.identifier[0]
        md.identification.uricode = imd.identifier
        md.identification.resourcelanguage = imd.resource_language
        md.identification.topiccategory = imd.topic_category

        # Keyword/Keyword (GIMED):
        for it in imd.keywords:
            kw = {}
            kw['keywords'] = it.get('terms')
            kw['type'] = None
            kw['thesaurus'] = {}
            kw['thesaurus']['date'] = it.get('date')
            kw['thesaurus']['datetype'] = it.get('datetype')
            kw['thesaurus']['title'] = it.get('name')
            md.identification.keywords.append(kw)

        md.identification.extent.boundingBox.miny = imd.bounding_box[0].sblat
        md.identification.extent.boundingBox.maxy = imd.bounding_box[0].nblat
        md.identification.extent.boundingBox.minx = imd.bounding_box[0].wblng
        md.identification.extent.boundingBox.maxx = imd.bounding_box[0].eblng

        md.identification.temporalextent_start = imd.temporal_extent[0].start
        md.identification.temporalextent_end = imd.temporal_extent[0].end

        val = CI_Date()
        val.date = imd.publication_date
        val.type = 'publication'
        md.identification.date.append(val)

        val = CI_Date()
        val.date = imd.creation_date
        val.type = 'creation'
        md.identification.date.append(val)

        val = CI_Date()
        val.date = imd.revision_date
        val.type = 'revision'
        md.identification.date.append(val)

        md.identification.denominators = imd.denominator
        for k in imd.spatial_resolution:
            md.identification.denominators.append(k.distance)
            md.identification.denominators.append(k.uom)

        md.dataquality.lineage = imd.lineage

        for k in imd.conformity:
            md.dataquality.conformancetitle.append(k.title)
            md.dataquality.conformancedate.append(k.date)
            md.dataquality.conformancedatetype.append(k.date_type)
            md.dataquality.conformancedegree.append(k.degree)


        md.identification.accessconstraints = 'otherRestrictions'
        md.identification.otherconstraints = imd.limitations

        md.identification.uselimitation = imd.access_constraints

        for it in imd.responsible_party:
            val = CI_ResponsibleParty()
            val.organization = it.organization
            val.email = it.email[0]
            val.role = it.role
            md.identification.contact.append(val)


        # Save custom record to a valid ISO XML file
        env = Environment(loader=FileSystemLoader('.'))
        env.globals.update(zip=zip)
        template = env.get_template('mdmetadata2iso.xml')
        iso_xml = template.render(md=md)
        xml_file = outfile
        xml_file = open(outfile, "w")
        xml_file.write(iso_xml)
        xml_file.close()

