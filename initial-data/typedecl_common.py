import zope.interface
from schema_common import *

class ResponsibleParty(object):
	zope.interface.implements(IResponsibleParty)	

	def __init__(self,organization,email,role):
		self.organization = organization
		self.email = email
		self.role = role
	def print_fields(self):
		print 'Org: %s' % self.organization
		print 'Email: %s' % self.email
		print 'Role: %s' % self.role

class FreeKeyword(object):
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


class GeographicBoundingBox(object):
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

class TemporalExtent(object):
	zope.interface.implements(ITemporalExtent)	

	def __init__(self,start,end):
		self.start = start
		self.end = end
	def print_fields(self):
		print 'Start date: %s' % self.start
		print 'End date: %s' % self.end

class SpatialResolution(object):
	zope.interface.implements(ISpatialResolution)	

	def __init__(self,denominator,distance,uom):
		self.denominator = denominator
		self.distance = distance
		self.uom = uom
	def print_fields(self):
		print 'Denominator: %s' % self.denominator
		print 'Distance: %s' % self.distance
		print 'Uom: %s' % self.uom

class Conformity(object):
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

