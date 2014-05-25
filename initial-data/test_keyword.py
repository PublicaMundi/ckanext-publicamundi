import zope.interface
import zope.schema
import datetime
from typedecl import *

print 'Testing IOriginatingVocabulary\n'

psoc = [OriginatingVocabulary("non unicode Title",datetime.date.today(),"creationn"),OriginatingVocabulary(u"Title",datetime.date(2014,01,01),"creation")]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IOriginatingVocabulary,poc)
	
print 'Testing IFreeKeyword\n'

psoc = [FreeKeyword(None,OriginatingVocabulary("non unicode Title",datetime.date.today(),"creationn")),FreeKeyword(u"asdsad",OriginatingVocabulary(u"Title",datetime.date(2014,01,01),"creation"))]
i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IFreeKeyword,poc)
	
print 'Testing IInspireKeyword\n'

psoc = [InspireKeyword(FreeKeyword("keyword",OriginatingVocabulary(u"title",datetime.date.today(),"creation")),[{'gemet_conceptss':['123']},{'gemet_concepts':['accident']}]),

InspireKeyword(FreeKeyword(u"keyword2",OriginatingVocabulary(u"title",datetime.date.today(),"creation")),[{'gemet_concepts':['buildings','addresses']}]),

InspireKeyword(FreeKeyword(u"keyword3",OriginatingVocabulary(u"title",datetime.date.today(),"creation")),[{'inspire_data_themes':[]}]),

InspireKeyword(FreeKeyword(u"keyword3",OriginatingVocabulary(u"title",datetime.date.today(),"creation")),[{'inspire_data_themes':['123']}])]

i = 1
for poc in psoc:
	print 'Test Case #%i \n' % i
	i+=1
	print 'input:'  
	poc.print_fields()
	print 'validation errors:%s\n' % zope.schema.getValidationErrors(IInspireKeyword,poc)
	

