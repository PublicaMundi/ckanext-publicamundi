import zope.interface
import zope.schema
import datetime
from typedecl_common import *

def test_resp_party_1():
    print '\nTesting Responsible Party\n'
    # Fixtures
    rp1 = ResponsibleParty("Non unicode name","non unicode email","Author")

    #print 'Test Case #%i \n' % i
    #i+=1
    print 'input:'  
    rp1.print_fields()
    #print 'validation errors:%s\n' % zope.schema.getValidationErrors(IResponsibleParty,poc)
    assert (not zope.schema.getValidationErrors(IResponsibleParty,rp1))

def test_resp_party_2():
    print '\nTesting Responsible Party\n'
    rp2 = ResponsibleParty(u"unicode name",["unicodenon@email"],"authorr")
    print 'input:'  
    rp2.print_fields()
    #print 'validation errors:%s\n' % zope.schema.getValidationErrors(IResponsibleParty,poc)
    assert (not zope.schema.getValidationErrors(IResponsibleParty,rp2))

def test_resp_party_3():
    print '\nTesting Responsible Party\n'
    rp3 = ResponsibleParty(u"org",[u"correct@email.com"],"author")
    print 'input:'  
    rp3.print_fields()
    #print 'validation errors:%s\n' % zope.schema.getValidationErrors(IResponsibleParty,poc)
    assert (not zope.schema.getValidationErrors(IResponsibleParty,rp3))

