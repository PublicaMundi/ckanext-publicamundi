import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.schemata import *
from ckanext.publicamundi.lib.metadata.schemata.common import *

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

@object_null_adapter(IResponsibleParty)
class ResponsibleParty(Object):
	zope.interface.implements(IResponsibleParty)

	def __init__(self,organization,email,role):
		self.organization = organization
		self.email = email
		self.role = role
	def print_fields(self):
		print 'Org: %s' % self.organization
		print 'Email: %s' % self.email
		print 'Role: %s' % self.role

@object_null_adapter(IFreeKeyword)
class FreeKeyword(Object):
	zope.interface.implements(IFreeKeyword)	

	def __init__(self,value,originating_vocabulary,reference_date,date_type):
		self.value = value
		self.originating_vocabulary = originating_vocabulary
		self.reference_date = reference_date
		self.date_type = date_type
	def print_fields(self):
		print 'Value: %s' % self.value
		print 'Originating vocab: %s' % self.originating_vocabulary
		print 'Ref Dat: %s' % self.reference_date
		print 'Date type: %s' % self.date_type


@object_null_adapter(IGeographicBoundingBox)
class GeographicBoundingBox(Object):
	zope.interface.implements(IGeographicBoundingBox)	

	def __init__(self,nblat,sblat,eblng,wblng):
		self.nblat = nblat
		self.sblat = sblat
		self.eblng = eblng
		self.wblng = wblng
	def print_fields(self):
		print 'North lat: %s' % self.nblat
		print 'South lat: %s' % self.sblat
		print 'East lng: %s' % self.eblng
		print 'West lng: %s' % self.wblng

@object_null_adapter(ITemporalExtent)
class TemporalExtent(Object):
	zope.interface.implements(ITemporalExtent)	

	def __init__(self,start,end):
		self.start = start
		self.end = end

@object_null_adapter(ISpatialResolution)
class SpatialResolution(Object):
	zope.interface.implements(ISpatialResolution)	

	def __init__(self,distance,uom):
		self.distance = distance
		self.uom = uom
	def print_fields(self):
		print 'Distance: %s' % self.distance
		print 'Uom: %s' % self.uom

@object_null_adapter(IConformity)
class Conformity(Object):
	zope.interface.implements(IConformity)	

	def __init__(self,title,date,date_type,degree):
		self.title = title
		self.date = date
		self.date_type = date_type
		self.degree = degree
	def print_fields(self):
		print 'title: %s' % self.title
		print 'Date: %s' % self.date
		print 'Date type: %s' % self.date_type
		print 'Degree: %s' % self.degree

