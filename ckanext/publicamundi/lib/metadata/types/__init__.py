import zope.interface
from unidecode import unidecode

from ckan.lib.munge import (munge_name, munge_title_to_name) 

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata import *


class BaseMetadata(Object):
    
    zope.interface.implements(IBaseMetadata)
    
    def deduce_basic_fields(self):
        transliterated_title = unidecode(self.title)
        return {
            'title': self.title,
            'name': munge_title_to_name(transliterated_title),
        }    

# Import types into our namespace

from ckanext.publicamundi.lib.metadata.types._common import *
from ckanext.publicamundi.lib.metadata.types.thesaurus import Thesaurus, ThesaurusTerms
from ckanext.publicamundi.lib.metadata.types.ckan_metadata import CkanMetadata
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import InspireMetadata
from ckanext.publicamundi.lib.metadata.types.foo import Foo
from ckanext.publicamundi.lib.metadata.types.baz import Baz

