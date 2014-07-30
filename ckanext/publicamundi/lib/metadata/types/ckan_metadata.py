import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.schemata.ckan_metadata import ICkanMetadata

from ckanext.publicamundi.lib.metadata.types import object_null_adapter
from ckanext.publicamundi.lib.metadata.types import BaseMetadata
from ckanext.publicamundi.lib.metadata.types.common import *

@object_null_adapter(ICkanMetadata)
class CkanMetadata(BaseMetadata):
    zope.interface.implements(ICkanMetadata)

    title = None

