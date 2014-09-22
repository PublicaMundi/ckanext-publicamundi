import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata.ckan_metadata import ICkanMetadata

from ckanext.publicamundi.lib.metadata.types import BaseMetadata

@object_null_adapter()
class CkanMetadata(BaseMetadata):
    
    zope.interface.implements(ICkanMetadata)

    title = None

