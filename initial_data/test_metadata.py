import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing IPointOfContact\n'

psoc = [PointOfContact(None,[u"missing@name.com"]),PointOfContact("non-unicode name",["non-unicode-non-email"]),PointOfContact(u"correct name",[u"non-email",u"emaiL@gmail.com"]),PointOfContact(u"correct name",[u"correct@email.com"])]

i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IPointOfContact,poc)
	
print 'Testing Metadata\n'
# if date entered wrong datetime.date raises error
psoc = [InspireMetadata([PointOfContact(u"name",[u"email@email.com"]),PointOfContact(None,u"asdasd")],None,"English"),InspireMetadata([],datetime.date(2011,12,5),None), InspireMetadata([PointOfContact(u"name",[u"email@email.gr"])],None,None),InspireMetadata([PointOfContact(u"name",[u"email@email.gr"])],datetime.date(2015,12,5),"Greek"),InspireMetadata([PointOfContact(u"name",[u"email@email.gr"])],datetime.date.today(),"Frenc")]

i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getSchemaValidationErrors(IInspireMetadata,poc)

