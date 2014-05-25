import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing Responsible party\n'

psoc = [InspireResponsibleParty([]),InspireResponsibleParty([ResponsibleParty(PointOfContact("WrongOrg",["email@email.com"]),u"Userr"),ResponsibleParty(PointOfContact(u"Org",[u"email@email"]),"User")]),InspireResponsibleParty([ResponsibleParty(PointOfContact(u"Org",[u"email@email.com"]),"User")])]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireResponsibleParty,poc)

