import zope.interface

from ckan.plugins import toolkit 

from ckanext.publicamundi.lib.metadata.base import (
    Object, object_null_adapter,
    object_format_adapter, ObjectFormatter)

from ckanext.publicamundi.lib.metadata.schemata import *

_ = toolkit._


@object_null_adapter()
class PostalAddress(Object):
    
    zope.interface.implements(IPostalAddress)

    address = None
    postalcode = None

@object_null_adapter()
class ContactInfo(Object):
    
    zope.interface.implements(IContactInfo)

    email = None
    address = None

@object_null_adapter()
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

@object_null_adapter()
class Polygon(Object):

    zope.interface.implements(IPolygon)

    points = None
    name = None

@object_null_adapter()
class ResponsibleParty(Object):
    
    zope.interface.implements(IResponsibleParty)

    organization = None
    email = None
    role = None

@object_null_adapter()
class FreeKeyword(Object):
    
    zope.interface.implements(IFreeKeyword)

    value = None
    originating_vocabulary = None
    reference_date = None
    date_type = None

@object_null_adapter()
class GeographicBoundingBox(Object):
    
    zope.interface.implements(IGeographicBoundingBox)

    nblat = None
    sblat = None
    eblng = None
    wblng = None

@object_null_adapter()
class TemporalExtent(Object):
    
    zope.interface.implements(ITemporalExtent)

    start = None
    end = None

@object_format_adapter(ITemporalExtent, 'default')
class TemporalExtentFormatter(ObjectFormatter):

    def _format(self, obj, opts):
        s = _('From %(start)s To %(end)s') % dict(start=obj.start, end=obj.end)
        return u'<%s>' % s if opts.get('quote') else s

@object_null_adapter()
class SpatialResolution(Object):
    
    zope.interface.implements(ISpatialResolution)

    distance = None
    uom = None

@object_null_adapter()
class Conformity(Object):
    
    zope.interface.implements(IConformity)

    title = None
    date = None
    date_type = None
    degree = None

