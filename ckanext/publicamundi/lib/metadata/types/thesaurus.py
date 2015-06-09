import os
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary

from ckanext.publicamundi.lib.metadata import vocabularies
from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata.thesaurus import (
    IThesaurusTerms, IThesaurus)

class Thesaurus(Object):

    zope.interface.implements(IThesaurus)

    # Interface IThesaurus

    title = None
    reference_date = None
    date_type = None
    name = None
    version = None

    @property
    def vocabulary(self):
        vocab = vocabularies.get_by_name(self.name)
        return vocab.get('vocabulary') if vocab else None

    # Factory for Thesaurus

    @classmethod
    def lookup(cls, name=None, title=None, for_keywords=False):
        '''Lookup by name or title and return a Thesaurus instance.

        This is a factory method that tries to instantiate a Thesaurus object
        from a collection of well-known (mostly related to INSPIRE) vocabularies.
        '''
        
        vocab = None
        
        if (name is None) and title:
            name = vocabularies.normalize_thesaurus_title(title, for_keywords)
        
        if name:
            vocab = vocabularies.get_by_name(name)
        else:
            raise ValueError('Expected a name/title lookup')

        if vocab:
            kwargs = {
               'title': vocab.get('title'),
               'name': vocab.get('name'),
               'reference_date': vocab.get('reference_date'),
               'version' : vocab.get('version'),
               'date_type': vocab.get('date_type'),
            }
            return cls(**kwargs)
        else:
            raise ValueError('Cannot find a thesaurus named "%s"' %(name))

@object_null_adapter()
class ThesaurusTerms(Object):
    
    zope.interface.implements(IThesaurusTerms)

    thesaurus = Thesaurus 
    
    terms = list

    def iter_terms(self):
        vocabulary = self.thesaurus.vocabulary.by_value
        for t in self.terms:
            yield vocabulary.get(t)
    
    __iter__ = iter_terms



