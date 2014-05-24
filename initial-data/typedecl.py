import zope.interface
from schema import *

@zope.interface.implementer(IPointOfContact)
class PointOfContact(object):
		
	def __init__(self, organization_name, email):
		self.organization_name = organization_name
		self.email = email
	def print_fields(self):
		print '%s , %s ' % (self.organization_name, self.email)

@zope.interface.implementer(IInspireMetadata)
class InspireMetadata(object):

	def __init__(self,point_of_contact,metadata_date,metadata_language):
		self.point_of_contact = point_of_contact
		self.metadata_date = metadata_date
		self.metadata_language = metadata_language
	def print_fields(self):
		print 'Point Of Contact(organization, email):'
		for k in self.point_of_contact:
			print '(%s , %s) ' % (k.organization_name,k.email)
		print 'Date: %s ' % (self.metadata_date)
		print 'Language: %s ' % (self.metadata_language)
@zope.interface.implementer(IIdentifier)
class Identifier(object):
	def __init__(self,code, codespace):
		self.code = code
		self.codespace = codespace
	def print_fields(self):
		print 'Code: %s' % self.code
		print 'Codespace: %s' % self.codespace

@zope.interface.implementer(IInspireIdentification)
class InspireIdentification(object):

	def __init__(self, resource_title, identifier, resource_abstract, resource_locator, resource_language):
		self.resource_title = resource_title
		self.identifier = identifier
		self.resource_abstract = resource_abstract
		self.resource_locator = resource_locator
		self.resource_language = resource_language
	
	def print_fields(self):
		print 'Resource title: %s' % self.resource_title
		print 'Identifier (code,codespace):'
		for k in self.identifier:
			print '(%s, %s)' % (k.code, k.codespace)
		print 'Resource abstract: %s' % self.resource_abstract
		print 'Resource locator (linkage):'
		for k in self.resource_locator:
			print '(%s)' % k
		print 'Resource language: '
		for k in self.resource_language:
			print '%s' % k

			
@zope.interface.implementer(IGeographicBoundingBox)
class GeographicBoundingBox(object):
	def __init__(self, north_bound_latitude, south_bound_latitude, east_bound_longitude, west_bound_longitude):
		self.north_bound_latitude = north_bound_latitude
		self.south_bound_latitude = south_bound_latitude
		self.east_bound_longitude = east_bound_longitude
		self.west_bound_longitude = west_bound_longitude
	def print_fields(self):
		print 'North Lat: %d' %self.north_bound_latitude 
		print 'South Lat: %d' %self.south_bound_latitude 
		print 'East Lng: %d' %self.east_bound_longitude 
		print 'West Lng: %d' %self.west_bound_longitude 
		

@zope.interface.implementer(IInspireClassification)
class InspireClassification(object):
	def __init__(self, topic_category):
		self.topic_category = topic_category
	def print_fields(self):
		print 'Topic Category: %s' % self.topic_category

@zope.interface.implementer(IInspireGeographic)
class InspireGeographic(object):
	def __init__(self, geographic_bounding_box):
		self.geographic_bounding_box = geographic_bounding_box

		
