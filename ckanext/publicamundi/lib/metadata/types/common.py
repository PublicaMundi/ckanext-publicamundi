import zope.interface

from ckanext.publicamundi.lib.metadata.base import BaseObject
from ckanext.publicamundi.lib.metadata.schemata import *

class PostalAddress(BaseObject):
    zope.interface.implements(IPostalAddress)
    
    address = None 
    postalcode = None

class ContactInfo(BaseObject):
    zope.interface.implements(IContactInfo)
    
    email = None
    address = None

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

class Polygon(BaseObject):
    zope.interface.implements(IPolygon)
    
    points = None
    name = None

class TemporalExtent(BaseObject):
    zope.interface.implements(ITemporalExtent)
    
    start = None
    end = None

