import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing Classification\n'

psoc = [InspireClassification(u"Biota"),InspireClassification("Biota"),InspireClassification("Envinroment"),InspireClassification("Environment")]


i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireClassification,poc)
