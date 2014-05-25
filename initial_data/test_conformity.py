import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing Conformity\n'

psoc = [InspireConformity([Conformity(u"spec",datetime.date(2015,01,01),"creation","Non conformant")])]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireConformity,poc)

