import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing Constraints\n'

psoc = [InspireConstraints([],["nonunicodelimitation",u"unicodelimitation",None]),InspireConstraints([u"lala"],[u"unicodelimitation"])]

i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireConstraints,poc)

