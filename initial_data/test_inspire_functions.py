import zope.interface
import zope.schema
import datetime
#from typedecl_common import *
#from typedecl import *
#from ckanext.publicamundi.lib.metadata.common import * 
from ckanext.publicamundi.lib.metadata.types import *
def typical_tests():
 
	psoc1 = InspireMetadata(
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
	
	psoc2 = InspireMetadata(
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
	
	psoc3 = InspireMetadata(
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
		datetime.date(2013,1,1),
		datetime.date(2013,1,1),
		datetime.date(2014,1,1),
		u"lineaage",
		[0,1,2,3],
		[SpatialResolution(None,u"meters")],
		[Conformity(u"specifications blabla",datetime.date.today(),"creation","conformant")],
		[u"lalala1",u"lalala2"],
		[u"limit1",u"limit2"],
		[ResponsibleParty(u"Org",[u"email@asd.gr"],"pointofcontact"),ResponsibleParty(u"Org2",[u"email2@asd.gr"],"pointofcontact")])

	test_inspire(psoc1,'all correct','test.xml')
	test_inspire(psoc2,'date invariants (upper level)','test2.xml')
	test_inspire(psoc3,'date invariants (lower level temporal extent + spatial resolution)','test3.xml')

def test_inspire(psoc,message,outfile):
	
	print 'Testing Metadata\n'

	print 'Test Case: ', message

	
	print 'input:'  
	psoc.print_fields()
	errorlist = zope.schema.getValidationErrors(IInspireMetadata,psoc)

	if errorlist == []:
	    print 'Validation Success!\n'
	    InspireMetadata.to_xml(psoc,outfile)
	else:
	    print 'Validation Failed.\n Errors = %s\n' % errorlist


