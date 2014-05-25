import zope.interface

from ckanext.publicamundi.lib.metadata.base import BaseObject
from ckanext.publicamundi.lib.metadata.schemata import *
from ckanext.publicamundi.lib.metadata.types import BaseMetadata
from ckanext.publicamundi.lib.metadata.types.common import *

class CkanMetadata(BaseMetadata):
    zope.interface.implements(ICkanMetadata)

    title = None

class InspireMetadata(BaseMetadata):
    zope.interface.implements(IInspireMetadata)
    
    title = None
    url = None
    thematic_category = None
    tags = list
    baz = None
    contact_info = ContactInfo
    contacts = dict
    geometry = list

