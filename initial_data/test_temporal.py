import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing Temporal extent\n'

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

print 'Testing Temporal\n'

psoc = [InspireTemporal([TemporalExtent(datetime.date(2000,01,01),datetime.date.today())],datetime.date.today(),datetime.date.today(), datetime.date(2015,01,01)),InspireTemporal([TemporalExtent(datetime.date(2000,01,01),datetime.date.today())],datetime.date.today(),datetime.date(2013,01,01),datetime.date(2012,01,01)),
InspireTemporal([TemporalExtent(datetime.date(2000,01,01),datetime.date.today()),TemporalExtent(datetime.date(2011,01,01),datetime.date.today())],datetime.date(2013,01,01),datetime.date(2014,01,01),datetime.date.today())]


i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireTemporal,poc)
