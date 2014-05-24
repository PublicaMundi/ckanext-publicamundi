import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing Geographic\n'

psoc = [GeographicBoundingBox(50,50,40,30),GeographicBoundingBox(-123.0,0.0,123.123,1235.0),GeographicBoundingBox(-50.0,-20.12,0.0,15.0)]


i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IGeographicBoundingBox,poc)
