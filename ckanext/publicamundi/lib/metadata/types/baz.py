import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata import IBaz

from . import Metadata, Thesaurus, ThesaurusTerms
from ._common import *

thesaurus_gemet_themes = Thesaurus.lookup('keywords-gemet-themes')

class KeywordsFactory(object):
    
    def __init__(self, thesaurus):
        self.thesaurus = thesaurus
    
    def __call__(self):
        return ThesaurusTerms(terms=[], thesaurus=self.thesaurus)

@object_null_adapter()
class Baz(Metadata):

    zope.interface.implements(IBaz)

    url = None
    
    contacts = list
    
    keywords = KeywordsFactory(thesaurus_gemet_themes)
    
    bbox = GeographicBoundingBox
