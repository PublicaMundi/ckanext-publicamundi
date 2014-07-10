import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.schemata import *

from ckanext.publicamundi.lib.metadata.types import object_null_adapter
from ckanext.publicamundi.lib.metadata.types import BaseMetadata
from ckanext.publicamundi.lib.metadata.types.common import *

@object_null_adapter(ICkanMetadata)
class CkanMetadata(BaseMetadata):
    zope.interface.implements(ICkanMetadata)

    title = None

#@object_null_adapter(IInspireMetadata)
#class InspireMetadata(BaseMetadata):
#    zope.interface.implements(IInspireMetadata)
#
#    title = None
