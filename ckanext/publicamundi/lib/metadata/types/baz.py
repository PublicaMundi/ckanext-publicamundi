import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata import IBaz

from ckanext.publicamundi.lib.metadata.types import BaseMetadata
from ckanext.publicamundi.lib.metadata.types import Thesaurus, ThesaurusTerms
from ckanext.publicamundi.lib.metadata.types._common import *

thesaurus_gemet_themes = Thesaurus.make('keywords-gemet-themes')

class KeywordsFactory(object):
    
    def __init__(self, thesaurus):
        self.thesaurus = thesaurus
    
    def __call__(self):
        return ThesaurusTerms(terms=[], thesaurus=self.thesaurus)

@object_null_adapter()
class Baz(BaseMetadata):

    zope.interface.implements(IBaz)

    url = None
    
    contacts = list
    
    keywords = KeywordsFactory(thesaurus_gemet_themes)
    
    bbox = GeographicBoundingBox
