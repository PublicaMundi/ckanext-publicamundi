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
[{'terms':[],'value':"gemet_inspire_data_themes"}], 
[GeographicBoundingBox(0.0,0.0,0.0,0.0)], 
[TemporalExtent(datetime.date(2012,1,1),datetime.date(2013,1,1))],
datetime.date(2012,1,1),
datetime.date(2013,1,1),
datetime.date(2014,1,1),
u"lineaage",
[SpatialResolution(0,0,u"meters")],
[Conformity(u"specifications blabla",datetime.date.today(),"creation","conformant")],
[u"lalala1",u"lalala2"],
[u"limit1",u"limit2"],
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact")])

print 'input:'  
psoc.print_fields()
print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireMetadata,psoc)

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
[{'terms':["lala"],'value':"gemet_inspire_data_themes"}], 
[GeographicBoundingBox(0.0,0.0,0.0,0.0)], 
[TemporalExtent(datetime.date(2012,1,1),datetime.date(2013,1,1))],
datetime.date(2014,1,1),
datetime.date(2013,1,1),
datetime.date(2012,1,1),
u"lineaage",
[SpatialResolution(0,0,u"meters")],
[Conformity(u"specifications blabla",datetime.date.today(),"creation","conformant")],
[u"lalala1",u"lalala2"],
[u"limit1",u"limit2"],
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact")])

print 'input:'  
psoc.print_fields()
print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireMetadata,psoc)

print 'Test Case #3'
print 'Test date invariants (lower levels // TemporalExtent + SpatialResolution)\n'

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
[{'terms':["lala"],'value':"gemet_inspire_data_themes"}], 
[GeographicBoundingBox(0.0,0.0,0.0,0.0)], 
[TemporalExtent(datetime.date(2014,1,1),datetime.date(2012,1,1))],
datetime.date(2012,1,1),
datetime.date(2013,1,1),
datetime.date(2014,1,1),
u"lineaage",
[SpatialResolution(0,None,u"meters")],
[Conformity(u"specifications blabla",datetime.date.today(),"creation","conformant")],
[u"lalala1",u"lalala2"],
[u"limit1",u"limit2"],
[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact")])

print 'input:'  
psoc.print_fields()
print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireMetadata,psoc)



