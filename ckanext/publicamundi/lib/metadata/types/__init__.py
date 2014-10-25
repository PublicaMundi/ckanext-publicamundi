import zope.interface

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata import *


class BaseMetadata(Object):
    
    zope.interface.implements(IBaseMetadata)


# Import types into our namespace

from ckanext.publicamundi.lib.metadata.types._common import *
from ckanext.publicamundi.lib.metadata.types.thesaurus import Thesaurus, ThesaurusTerms
from ckanext.publicamundi.lib.metadata.types.ckan_metadata import CkanMetadata
from ckanext.publicamundi.lib.metadata.types.inspire_metadata import InspireMetadata
from ckanext.publicamundi.lib.metadata.types.foo import Foo
from ckanext.publicamundi.lib.metadata.types.baz import Baz

