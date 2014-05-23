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

class Identifier(BaseObject):
    zope.interface.implements(IIdentifier)
        
    code = None
    codespace = None
    
    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)

class GeographicBoundingBox(BaseObject):
    zope.interface.implements(IGeographicBoundingBox)
    
    northBoundLatitude = None
    southhBoundLatitude = None
    eastBoundLongitude = None
    westBoundLongitude = None
    
    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)

class InspireMetadata(BaseMetadata):
    zope.interface.implements(IInspireMetadata)
    
    metadataPointOfContact = list
    metadataDate = None
    metadataLanguage = None
    
    identificationResourceTitle = None
    identificationIdentifier = List
    identificationResourceAbstract = None
    identificationResourceLocator = List
    identificationResourceLanguage = List

    classificationTopicCategory = None

    geographicBoundingBox = GeographicBoundingBox
    geographicCountries = None
    
    def __init__(self, **kwargs):
        BaseMetadata.__init__(self, **kwargs)
