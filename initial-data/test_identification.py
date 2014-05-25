import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing Identifier\n'

psoc = [Identifier(None,None),Identifier("test-code","test-codespace"),Identifier(u"uni-code",u"uni-codespace"),Identifier("123456","test.com"),Identifier(u"123456","test.com")]

i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IIdentifier,poc)

print 'Testing Identification\n'

psoc = [InspireIdentification("non unicode title", [Identifier("123456","test.com"),Identifier(u"123456","test.com")], u"correct abstract\nwith\nseparate lines", ["http://www.google.com"], ["Greeklish"]), InspireIdentification(u"Correct title", [Identifier(u"123456","lala.lala")], u"abstract", [], []), InspireIdentification(u"Correct title", [], u"abstract", ["www.wrongurl.com"], ["French"]), InspireIdentification(u"correct title", [Identifier(u"23123123213","lala.com")], u"abstract", [], ["Greek","Spanglish"])]


i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireIdentification,poc)
