import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.schemata import *

class PostalAddress(Object):
    zope.interface.implements(IPostalAddress)

    address = None
    postalcode = None

class ContactInfo(Object):
    zope.interface.implements(IContactInfo)

    email = None
    address = None

class Point(Object):
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

class Polygon(Object):
    zope.interface.implements(IPolygon)

    points = None
    name = None

class TemporalExtent(Object):
    zope.interface.implements(ITemporalExtent)

    start = None
    end = None

