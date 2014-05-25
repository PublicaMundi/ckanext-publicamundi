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
	def __init__(self, geographic_bounding_box,geographic_countries):
		self.geographic_bounding_box = geographic_bounding_box
		self.geographic_countries = geographic_countries
	
	def print_fields(self):
		print 'Geographic Bounding Box (north lat, south lat, east lng, west lng):'
		for k in self.geographic_bounding_box:
			print '(%d, %d, %d, %d):' % (k.north_bound_latitude, k.south_bound_latitude, k.east_bound_longitude, k.west_bound_longitude) 
		print 'Geographic countries: %s' % self.geographic_countries 
	
	
@zope.interface.implementer(ITemporalExtent)
class TemporalExtent(object):
	def __init__(self, starting_date, ending_date):
		self.starting_date = starting_date
		self.ending_date = ending_date
	
	def print_fields(self):
		print 'Temporal extent (starting date, ending date):'
		print '(%s, %s):' % (self.starting_date, self.ending_date) 
@zope.interface.implementer(IInspireTemporal)
class InspireTemporal(object):
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


@zope.interface.implementer(ISpatialResolution)
class SpatialResolution(object):
	def __init__(self, equivalent_scale, resolution_distance, unit_of_measure):
		self.equivalent_scale = equivalent_scale
		self.resolution_distance = resolution_distance
		self.unit_of_measure = unit_of_measure

	def print_fields(self):
		print 'Equivalent scale: %d' % self.equivalent_scale
		print 'Resolution distance: %d' % self.resolution_distance
		print 'Unit of measure: %s' % self.unit_of_measure


@zope.interface.implementer(IInspireQualityValidity)
class InspireQualityValidity(object):

	def __init__(self, lineage, spatial_resolution):
		self.lineage = lineage
		self.spatial_resolution = spatial_resolution

	def print_fields(self):
		print 'Lineage: %s' % self.lineage
		print 'Spatial Resolution(equivalent scale, resolution distance, unit of measure):'
		for k in self.spatial_resolution:
			print '(%d %d %s)' % (k.equivalent_scale, k.resolution_distance, k.unit_of_measure)

@zope.interface.implementer(IConformity)
class Conformity(object):
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


@zope.interface.implementer(IInspireConformity)
class InspireConformity(object):
	def __init__(self,conformity):
		self.conformity = conformity
	def print_fields(self):
		print 'Conformity (specifications, date, date type, degree):'
		for k in self.conformity:
			print '(%s %s %s %s)' % (k.specifications, k.date, k.date_type, k.degree)
			
@zope.interface.implementer(IInspireConstraints)
class InspireConstraints(object):
	def __init__(self,conditions, limitations):
		self.conditions = conditions
		self.limitations = limitations
	def print_fields(self):
		print 'Conditions: %s' % self.conditions
		print 'Limitations: %s' % self.limitations

@zope.interface.implementer(IResponsibleParty)
class ResponsibleParty(object):
	def __init__(self,point_of_contact,party_role):
		self.point_of_contact = point_of_contact
		self.party_role = party_role
	
@zope.interface.implementer(IInspireResponsibleParty)
class InspireResponsibleParty(object):
	def __init__(self,responsible_party):
		self.responsible_party = responsible_party
	def print_fields(self):
		print 'Responsible party: (PoC, party_role)'
		for k in self.responsible_party:
			print '(%s)' % k.party_role
