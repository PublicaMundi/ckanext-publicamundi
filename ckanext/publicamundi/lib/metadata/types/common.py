import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.schemata import *

from ckanext.publicamundi.lib.metadata.types import object_null_adapter

@object_null_adapter(IPostalAddress)
class PostalAddress(Object):
    zope.interface.implements(IPostalAddress)

    address = None
    postalcode = None

@object_null_adapter(IContactInfo)
class ContactInfo(Object):
    zope.interface.implements(IContactInfo)

    email = None
    address = None

@object_null_adapter(IPoint)
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

@object_null_adapter(IPolygon)
class Polygon(Object):
    zope.interface.implements(IPolygon)

    points = None
    name = None

@object_null_adapter(ITemporalExtent)
class TemporalExtent(Object):
    zope.interface.implements(ITemporalExtent)

    start = None
    end = None

