import zope.interface
import zope.schema

import ckanext.publicamundi.lib
from ckanext.publicamundi.lib.metadata.base import BaseObject
from ckanext.publicamundi.lib.metadata.schema import *

class PointOfContact(BaseObject):
    zope.interface.implements(IPointOfContact)
    
    organizationName = None
    email = None

    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)

class InspireMetadata(BaseMetadata):
    zope.interface.implements(IInspireMetadata)
    
    metadataPointOfContact = list
    metadataDate = None
    metadataLanguage = None

    def __init__(self, **kwargs):
        BaseMetadata.__init__(self, **kwargs)
