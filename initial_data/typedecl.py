import zope.interface
from schema import *

class PointOfContact(object):
	zope.interface.implements(IPointOfContact)	
	def __init__(self, organization_name, email):
		self.organization_name = organization_name
		self.email = email
	def print_fields(self):
		print '%s , %s ' % (self.organization_name, self.email)

class InspireMetadata(object):
	zope.interface.implements(IInspireMetadata)	

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

class Identifier(object):
	zope.interface.implements(IIdentifier)	

	def __init__(self,code, codespace):
		self.code = code
		self.codespace = codespace
	def print_fields(self):
		print 'Code: %s' % self.code
		print 'Codespace: %s' % self.codespace

class InspireIdentification(object):
	zope.interface.implements(IInspireIdentification)	

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

			
class GeographicBoundingBox(object):
	zope.interface.implements(IGeographicBoundingBox)
	
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
		

class InspireClassification(object):
	zope.interface.implements(IInspireClassification)	
	
	def __init__(self, topic_category):
		self.topic_category = topic_category
	def print_fields(self):
		print 'Topic Category: %s' % self.topic_category

class InspireGeographic(object):
	zope.interface.implements(IInspireGeographic)	
	
	def __init__(self, geographic_bounding_box,geographic_countries):
		self.geographic_bounding_box = geographic_bounding_box
		self.geographic_countries = geographic_countries
	
	def print_fields(self):
		print 'Geographic Bounding Box (north lat, south lat, east lng, west lng):'
		for k in self.geographic_bounding_box:
			print '(%d, %d, %d, %d):' % (k.north_bound_latitude, k.south_bound_latitude, k.east_bound_longitude, k.west_bound_longitude) 
		print 'Geographic countries: %s' % self.geographic_countries 
	
	
class TemporalExtent(object):
	zope.interface.implements(ITemporalExtent)	

	def __init__(self, starting_date, ending_date):
		self.starting_date = starting_date
		self.ending_date = ending_date
	
	def print_fields(self):
		print 'Temporal extent (starting date, ending date):'
		print '(%s, %s):' % (self.starting_date, self.ending_date) 

class InspireTemporal(object):
	zope.interface.implements(IInspireTemporal)
	
	def __init__(self,temporal_extent, creation_date, publication_date, revision_date):
		self.temporal_extent = temporal_extent
		self.creation_date = creation_date
		self.publication_date = publication_date
		self.revision_date = revision_date
	
	def print_fields(self):
		print 'Temporal extent (starting date, ending date):'
		for k in self.temporal_extent:
			print '(%s, %s):' % (k.starting_date, k.ending_date) 
		print 'Creation date: %s' % self.creation_date
		print 'Publication date: %s' % self.publication_date
		print 'Last revision date: %s' % self.revision_date 


class SpatialResolution(object):
	zope.interface.implements(ISpatialResolution)
	
	def __init__(self, equivalent_scale, resolution_distance, unit_of_measure):
		self.equivalent_scale = equivalent_scale
		self.resolution_distance = resolution_distance
		self.unit_of_measure = unit_of_measure

	def print_fields(self):
		print 'Equivalent scale: %d' % self.equivalent_scale
		print 'Resolution distance: %d' % self.resolution_distance
		print 'Unit of measure: %s' % self.unit_of_measure


class InspireQualityValidity(object):
	zope.interface.implements(IInspireQualityValidity)	

	def __init__(self, lineage, spatial_resolution):
		self.lineage = lineage
		self.spatial_resolution = spatial_resolution

	def print_fields(self):
		print 'Lineage: %s' % self.lineage
		print 'Spatial Resolution(equivalent scale, resolution distance, unit of measure):'
		for k in self.spatial_resolution:
			print '(%d %d %s)' % (k.equivalent_scale, k.resolution_distance, k.unit_of_measure)

class Conformity(object):
	zope.interface.implements(IConformity)	
	
	def __init__(self,specifications, date, date_type, degree):
		self.specifications = specifications
		self.date = date
		self.date_type = date_type
		self.degree = degree
	def print_fields(self):
		print 'Specifications: %s' % self.specifications
		print 'Date: %s' % self.date
		print 'Date type: %s' % self.date_type
		print 'Degree: %s' % self.degree


class InspireConformity(object):
	zope.interface.implements(IInspireConformity)
	
	def __init__(self,conformity):
		self.conformity = conformity
	def print_fields(self):
		print 'Conformity (specifications, date, date type, degree):'
		for k in self.conformity:
			print '(%s %s %s %s)' % (k.specifications, k.date, k.date_type, k.degree)
			
class InspireConstraints(object):
	zope.interface.implements(IInspireConstraints)	

	def __init__(self,conditions, limitations):
		self.conditions = conditions
		self.limitations = limitations
	def print_fields(self):
		print 'Conditions: %s' % self.conditions
		print 'Limitations: %s' % self.limitations

class ResponsibleParty(object):
	zope.interface.implements(IResponsibleParty)
	
	def __init__(self,point_of_contact,party_role):
		self.point_of_contact = point_of_contact
		self.party_role = party_role
	
class InspireResponsibleParty(object):
	zope.interface.implements(IInspireResponsibleParty)
	
	def __init__(self,responsible_party):
		self.responsible_party = responsible_party
	def print_fields(self):
		print 'Responsible party: (PoC, party_role)'
		for k in self.responsible_party:
			print '(%s)' % k.party_role

class FreeKeyword(object):
	zope.interface.implements(IFreeKeyword)
	
	def __init__(self,keyword_value,originating_vocabulary):
		self.keyword_value = keyword_value
		self.originating_vocabulary = originating_vocabulary
	def print_fields(self):
		print 'Keyword value: %s' % self.keyword_value

class OriginatingVocabulary(object):
	zope.interface.implements(IOriginatingVocabulary)
	
	def __init__(self,title,reference_date, date_type):
		self.title = title
		self.reference_date = reference_date
		self.date_type = date_type
	def print_fields(self):
		print 'Title: %s' % self.title
		print 'Reference date: %s' % self.reference_date
		print 'Date type: %s' % self.date_type

class InspireKeyword(object):
	zope.interface.implements(IInspireKeyword)
	
	def __init__(self,free_keyword,keywords):
		self.keywords = keywords
		self.free_keyword = free_keyword
	def print_fields(self):
		print 'Free keyword: '
		print '(%s)' % (self.free_keyword.keyword_value)
		print 'All keywords:'
		print '(%s) ' % (self.keywords)
