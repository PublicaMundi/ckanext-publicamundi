import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.base import BaseObject
from ckanext.publicamundi.lib.metadata.schema import *

# Note:
# All classes we want to export as null factories should be globally 
# registered as null adapters. 

class BaseMetadata(BaseObject):
    pass

class PostalAddress(BaseObject):
    zope.interface.implements(IPostalAddress)
    
    address = None 
    postalcode = None

    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)

adapter_registry.register([], IPostalAddress, '', PostalAddress)

class ContactInfo(BaseObject):
    zope.interface.implements(IContactInfo)
    
    email = None
    address = None

    def __init__(self, **kwargs):
        BaseObject.__init__(self, **kwargs)

adapter_registry.register([], IContactInfo, '', ContactInfo)

class Point(BaseObject):
    zope.interface.implements(IPoint)
    
    x = None
    y = None

    def __repr__(self):
        return '<Point x=%.1f y=%.2f>' %(self.x, self.y)
    
    def __eq__(self, other):
        if isinstance(other, Point): 
            return self.x == other.x and self.y == other.y
        else:
            return False

adapter_registry.register([], IPoint, '', Point)

class Polygon(BaseObject):
    zope.interface.implements(IPolygon)
    
    points = None
    name = None

adapter_registry.register([], IPolygon, '', Polygon)

class CkanMetadata(BaseMetadata):
    zope.interface.implements(ICkanMetadata)

    title = None
    
    def __init__(self, **kwargs):
        BaseMetadata.__init__(self, **kwargs)

adapter_registry.register([], ICkanMetadata, '', CkanMetadata)

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

    def __init__(self, **kwargs):
        BaseMetadata.__init__(self, **kwargs)

adapter_registry.register([], IInspireMetadata, '', InspireMetadata)

