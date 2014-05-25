import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing Spatial resolution\n'

psoc = [SpatialResolution(5,5,"lalal"),SpatialResolution(5.4,3,u"asdad"),SpatialResolution(5,5,u"asdasd")]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(ISpatialResolution,poc)

print 'Testing Quality and Validity\n'

psoc = [ InspireQualityValidity("non-unicode",[SpatialResolution(5,5,u"correct"),SpatialResolution(0,0,None)]),InspireQualityValidity(u'correct', [SpatialResolution(5,5,u"ok")])]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireQualityValidity,poc)

