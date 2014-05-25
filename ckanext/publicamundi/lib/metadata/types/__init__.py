import zope.interface

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.base import BaseObject
from ckanext.publicamundi.lib.metadata.schemata import *

class BaseMetadata(BaseObject):
    zope.interface.implements(IBaseMetadata)

# Import types

from ckanext.publicamundi.lib.metadata.types.common import *
from ckanext.publicamundi.lib.metadata.types.metadata import *

# Register null adapters (implementers) for needed interfaces

adapter_registry.register([], IPostalAddress, '', PostalAddress)

adapter_registry.register([], IContactInfo, '', ContactInfo)

adapter_registry.register([], IPoint, '', Point)

adapter_registry.register([], IPolygon, '', Polygon)

adapter_registry.register([], ICkanMetadata, '', CkanMetadata)

adapter_registry.register([], IInspireMetadata, '', InspireMetadata)

