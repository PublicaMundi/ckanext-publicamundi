import zope.interface
import zope.schema
import datetime
from typedecl_common import *

print '\nTesting Responsible Party\n'

psoc = [ResponsibleParty("Non unicode name","non unicode email","Author"),ResponsibleParty(u"unicode name",["unicodenon@email"],"authorr"),ResponsibleParty(u"org",[u"correct@email.com"],"author"),]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IResponsibleParty,poc)

print 'Testing Conformity\n'

psoc = [Conformity(u"lala",datetime.date(2015,1,1),"creationn","confofrmant"),Conformity(u"lala",datetime.date.today(),"creation","conformant")]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IConformity,poc)

print 'Testing Free keywords\n'

psoc = [FreeKeyword(u"val",None,datetime.date(2012,1,1),"creationn"),FreeKeyword(None,u"original",datetime.date.today(),'creation'),FreeKeyword(u"val",u"original",datetime.date.today(),'creation')]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IFreeKeyword,poc)

print 'Testing Geographic Bounding box\n'

psoc = [GeographicBoundingBox(50,50,40,30),GeographicBoundingBox(-123.0,0.0,123.123,1235.0),GeographicBoundingBox(-50.0,-20.12,0.0,15.0)]


i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IGeographicBoundingBox,poc)

print 'Testing Temporal\n'

psoc = [TemporalExtent(datetime.date(2015,01,01),datetime.date.today()),
TemporalExtent(datetime.date(2014,01,01),datetime.date(2013,01,01)),
TemporalExtent(datetime.date(2014,01,01),datetime.date.today())]

i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(ITemporalExtent,poc)

print 'Testing Spatial resolution\n'

psoc = [SpatialResolution(5,5,"lalal"),SpatialResolution(5.4,3,u"a"),SpatialResolution(5,5,u"asdasd")]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(ISpatialResolution,poc)

print 'Testing Conformity\n'

psoc = [Conformity(u"spec",datetime.date(2015,01,01),"creation","Non conformant"),Conformity(u"a",datetime.date.today(),"creation","not_conformant")]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IConformity,poc)

