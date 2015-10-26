import zope.interface
from unidecode import unidecode

from ckan.lib.munge import (munge_name, munge_title_to_name) 

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata import *


class BaseMetadata(Object):
    
    zope.interface.implements(IBaseMetadata)
    
    def deduce_fields(self, keys=()):
        # Todo: Adapt to new key-based contract
        transliterated_title = unidecode(self.title)
        return {
            'title': self.title,
            'name': munge_title_to_name(transliterated_title),
        }    

# Import types into our namespace

from ._common import *
from .thesaurus import Thesaurus, ThesaurusTerms
from .ckan_metadata import CkanMetadata
from .inspire_metadata import InspireMetadata
from .foo import Foo
from .baz import Baz

