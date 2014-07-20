import copy
import json
import datetime
import zope.interface
from zope.interface.verify import verifyObject
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi.lib.metadata.schemata.inspire import *
from ckanext.publicamundi.lib.metadata.types.inspire import *

from ckanext.publicamundi.tests.helpers import assert_faulty_keys

thesaurus1 = Thesaurus(
    title = u'GEMET Concepts',
    name = 'keywords-gemet-concepts',
    reference_date = datetime.date(2014, 1, 1),
    date_type = 'creation'
)

terms11 = ThesaurusTerms(
    thesaurus = thesaurus1,
    terms = ['accident', 'atmosphere']
)

terms12 = ThesaurusTerms(
    thesaurus = thesaurus1,
    terms = ['accident', 'foo']
)

def test_11():
    verifyObject(IThesaurus, thesaurus1)
    verifyObject(IThesaurusTerms, terms11)
    
    for k in thesaurus1.vocabulary: 
        print k.title, k.value

    assert_faulty_keys(thesaurus1, expected_keys=[])
    assert_faulty_keys(terms11, expected_keys=[])

    print ' -- to_dict --'
    print terms11.to_dict()
    print ' -- to_dict flat --'
    print terms11.to_dict(flat=True)

def test_12():
    assert_faulty_keys(terms12, expected_keys=['__after'])

if __name__ == '__main__':
    test_11()
    test_12()


