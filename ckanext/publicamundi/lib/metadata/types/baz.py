import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata import IBazMetadata

from . import Metadata, deduce, dataset_type 
from ._common import *
from .thesaurus import Thesaurus, ThesaurusTerms

thesaurus_gemet_themes = Thesaurus.lookup('keywords-gemet-themes')

class KeywordsFactory(object):
    
    def __init__(self, thesaurus):
        self.thesaurus = thesaurus
    
    def __call__(self):
        return ThesaurusTerms(terms=[], thesaurus=self.thesaurus)

@dataset_type('baz')
@object_null_adapter()
class BazMetadata(Metadata):

    zope.interface.implements(IBazMetadata)

    @property
    def identifier(self):
        return self.url
    
    url = None
    contacts = list
    keywords = KeywordsFactory(thesaurus_gemet_themes)
    bbox = GeographicBoundingBox

