import copy
import json
import datetime
import zope.interface
from zope.interface.verify import verifyObject
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi.lib.metadata.schemata.inspire_metadata import *
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import *

from ckanext.publicamundi.tests.helpers import assert_faulty_keys

# Thesaurus pointing to "Gemet Concepts" vocabulary
thesaurus_gemet_concepts = Thesaurus(
    title = u'GEMET Concepts',
    name = 'keywords-gemet-concepts',
    reference_date = datetime.date(2014, 1, 1),
    date_type = 'creation'
)

# Thesaurus does not exist
thesaurus_baz = Thesaurus(
    title = u'Baz',
    name = 'keywords-baz',
    reference_date = datetime.date(2014, 1, 1),
    date_type = 'creation'
)

def test_11():
    terms11 = ThesaurusTerms(
        thesaurus = thesaurus_gemet_concepts,
        terms = ['accident', 'atmosphere']
    )

    verifyObject(IThesaurus, thesaurus_gemet_concepts)
    verifyObject(IThesaurusTerms, terms11)
    
    for k in thesaurus_gemet_concepts.vocabulary: 
        print k.title, k.value

    assert_faulty_keys(thesaurus_gemet_concepts, expected_keys=[])
    assert_faulty_keys(terms11, expected_keys=[])

    print ' -- to_dict --'
    print terms11.to_dict()
    print ' -- to_dict flat --'
    print terms11.to_dict(flat=True)

def test_12():
    terms12 = ThesaurusTerms(
        thesaurus = thesaurus_gemet_concepts,
        terms = ['accident', 'foo']
    )

    assert_faulty_keys(terms12,
        expected_keys = ['__after'], 
        expected_invariants=['The following terms dont belong to thesaurus'])

def test_13():
    terms13 = ThesaurusTerms() 
    
    assert_faulty_keys(terms13,
        expected_keys=['terms', 'thesaurus'])

def test_14():
    terms14 = ThesaurusTerms(
        terms = ['foo']
    ) 
    
    assert_faulty_keys(terms14,
        expected_keys=['thesaurus'])

def test_15():
    terms15 = ThesaurusTerms(
        thesaurus = 'i am not a thesaurus object',
        terms = ['foo']
    ) 
    
    assert_faulty_keys(terms15,
        expected_keys=['thesaurus'])

def test_16():
    terms16 = ThesaurusTerms(
        thesaurus = thesaurus_gemet_concepts,
    ) 

    assert_faulty_keys(terms16,
        expected_keys=['terms'])

def test_17():
    '''Provide a non-existent vocabulary'''
    
    assert_faulty_keys(thesaurus_baz,
        expected_keys=['vocabulary'])
    
    terms17 = ThesaurusTerms(
        thesaurus = thesaurus_baz,
        terms = ['baz-1', 'baz-2']
    ) 

    assert_faulty_keys(terms17,
        expected_keys=['thesaurus'])


if __name__ == '__main__':
    test_11()


