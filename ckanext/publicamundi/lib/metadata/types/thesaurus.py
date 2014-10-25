import os
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary

from ckanext.publicamundi.lib.metadata.vocabularies import inspire_vocabularies
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
        spec = inspire_vocabularies.get_by_name(self.name)
        return spec.get('vocabulary') if spec else None

    # Factory for Thesaurus

    @classmethod
    def make(cls, name):
        '''Create a new Thesaurus instance from it's machine-name name.
        '''
        spec = inspire_vocabularies.get_by_name(name)
        if spec:
            kwargs = {
               'title': spec.get('title'),
               'name': spec.get('name'),
               'reference_date': spec.get('reference_date'),
               'version' : spec.get('version'),
               'date_type': spec.get('date_type'),
            }
            return cls(**kwargs)
        else:
            raise ValueError(
                'Cannot find an INSPIRE thesaurus named "%s"' %(name))

@object_null_adapter()
class ThesaurusTerms(Object):
    
    zope.interface.implements(IThesaurusTerms)

    thesaurus = Thesaurus
    terms = list

