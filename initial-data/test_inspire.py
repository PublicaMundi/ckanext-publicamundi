import zope.interface
import zope.schema
import datetime
from typedecl_common import *
from typedecl import *

print 'Testing Metadata\n'
# if date entered wrong datetime.date raises error

###	def __init__(self,contact,datestamp,languagecode,title,identifier,abstract,locator,resource_language,topic_category,keywords, bounding_box,temporal_extent,creation_date,publication_date,revision_date,lineage,spatial_resolution,conformity,access_constraints,limitations,responsible_party):


print 'Test Case #1'
print 'all correct\n'

psoc = InspireMetadata(
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact")],
datetime.date.today(),
"el",
u"Title",
[u"12314213123"],
u"abstracttttttt",
["http://www.google.com"],
["el"],
["biota"],
[{'terms':[],'value':"gemet_inspire_data_themes",'name':"Inspire Data Themes",'date':datetime.date(2012,1,1),'datetype':'creation'}], 
[GeographicBoundingBox(0.0,0.0,0.0,0.0)], 
[TemporalExtent(datetime.date(2012,1,1),datetime.date(2013,1,1))],
datetime.date(2012,1,1),
datetime.date(2013,1,1),
datetime.date(2014,1,1),
u"lineaage",
[0,1,2],
[SpatialResolution(0,u"meters")],
[Conformity(u"specifications blabla",datetime.date.today(),"creation","conformant")],
[u"lalala1",u"lalala2"],
[u"limit1",u"limit2"],
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact")])

print 'input:'  
psoc.print_fields()
errorlist = zope.schema.getValidationErrors(IInspireMetadata,psoc)

if errorlist == []:
    print 'Validation Success!\n'
    InspireMetadata.to_xml(psoc,"1.xml")
else:
    print 'Validation Failed.\n Errors = %s\n' % errorlist

print 'Test Case #2'
print 'Test date invariants (upper level)\n'

psoc = InspireMetadata(
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact")],
datetime.date.today(),
"el",
u"Title",
[u"12314213123"],
u"abstracttttttt",
["http://www.google.com"],
["el"],
["biota"],
[{'terms':["lala"],'value':"gemet_inspire_data_themes",'name':"Inspire Data Themes",'date':datetime.date(1000,1,1),'datetype':'creation'}], 
[GeographicBoundingBox(0.0,0.0,0.0,0.0)], 
[TemporalExtent(datetime.date(2012,1,1),datetime.date(2013,1,1))],
datetime.date(2014,1,1),
datetime.date(2013,1,1),
datetime.date(2012,1,1),
u"lineaage",
[0,1,2],
[SpatialResolution(0,u"meters")],
[Conformity(u"specifications blabla",datetime.date.today(),"creation","conformant")],
[u"lalala1",u"lalala2"],
[u"limit1",u"limit2"],
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact")])

print 'input:'  
psoc.print_fields()

errorlist = zope.schema.getValidationErrors(IInspireMetadata,psoc)

if errorlist == []:
    print 'Validation Success!\n'
    InspireMetadata.to_xml(psoc,"2.xml")
else:
    print 'Validation Failed.\n Errors = %s\n' % errorlist

print 'Test Case #3'
print 'Test date invariants (lower levels // TemporalExtent + SpatialResolution)\n'

psoc = InspireMetadata(
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact")],
datetime.date.today(),
"el",
u"Title",
[u"12314213123"],
u"abstracttttttt",
["http://www.google.com","http://publicamundi.eu"],
["el"],
["biota"],
[{'terms':["lala1","lala2","lala3"],'value':"gemet_inspire_data_themes",'name':"Inspire Data Themes",'date':datetime.date(2000,1,1),'datetype':'creation'}],
[GeographicBoundingBox(0.0,0.0,0.0,0.0)], 
[TemporalExtent(datetime.date(2014,1,1),datetime.date(2012,1,1))],
datetime.date(2012,1,1),
datetime.date(2013,1,1),
datetime.date(2014,1,1),
u"lineaage",
[0,1,2,3],
[SpatialResolution(None,u"meters")],
[Conformity(u"specifications blabla",datetime.date.today(),"creation","conformant")],
[u"lalala1",u"lalala2"],
[u"limit1",u"limit2"],
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact"),ResponsibleParty(u"Org2",[u"email2@asd.gr"],"pointofcontact")])

print 'input:'  
psoc.print_fields()

errorlist = zope.schema.getValidationErrors(IInspireMetadata,psoc)
if errorlist == []:
    print 'Validation Success!\n'
    InspireMetadata.to_xml(psoc,"3.xml")

    print 'reading xml 3.xml'
    imd = InspireMetadata.from_xml("3.xml")
    print 'Inspire model ='
    print InspireMetadata.print_fields(imd)
    errorlist = zope.schema.getValidationErrors(IInspireMetadata,imd)
    if errorlist == []:
        print 'Validation Success!\n'
    else:
        print 'Validation Failed, %s' % errorlist

else:
    print 'Validation Failed.\n Errors = %s\n' % errorlist





