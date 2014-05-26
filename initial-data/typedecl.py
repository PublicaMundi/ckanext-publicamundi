import zope.interface
from schema import *


class InspireMetadata(object):
	zope.interface.implements(IInspireMetadata)	

	def __init__(self,contact,datestamp,languagecode,title,identifier,abstract,locator,resource_language,topic_category,keywords, bounding_box,temporal_extent,creation_date,publication_date,revision_date,lineage,spatial_resolution,conformity,access_constraints,limitations,responsible_party):
		self.contact = contact
		self.datestamp = datestamp
		self.languagecode = languagecode
		self.title = title
		self.identifier = identifier
		self.abstract = abstract
		self.locator = locator
		self.resource_language = resource_language
		self.topic_category = topic_category
		self.keywords = keywords
		self.bounding_box = bounding_box
		self.temporal_extent = temporal_extent
		self.creation_date = creation_date
		self.publication_date = publication_date
		self.revision_date = revision_date
		self.lineage = lineage
		self.spatial_resolution = spatial_resolution
		self.conformity = conformity
		self.access_constraints = access_constraints
		self.limitations = limitations
		self.responsible_party = responsible_party
	def print_fields(self):
		print 'Contact(organization, email,role):'
		for k in self.contact:
			print '(%s , %s, %s) ' % (k.organization,k.email, k.role)
		print 'Date: %s ' % (self.datestamp)
		print 'Language: %s ' % (self.languagecode)
		print 'Title: %s ' % (self.title)
		print 'Id: %s ' % (self.identifier)
		print 'Abstract: %s ' % (self.abstract)
		print 'Locator: %s ' % (self.locator)
		print 'Resource language: %s ' % (self.resource_language)
		print 'Topic category: %s ' % (self.topic_category)
		print 'Keywords: %s ' % (self.keywords)
		for k in self.bounding_box:
			print '(%d , %d, %d, %d) ' % (k.nblat,k.sblat, k.eblng,k.wblng)
		for k in self.temporal_extent:
			print '(%s, %s) ' % (k.start,k.end)
		print 'Creation date: %s ' % (self.creation_date)
		print 'Publication date: %s ' % (self.publication_date)
		print 'Revision date: %s ' % (self.revision_date)
		print 'Lineage: %s ' % (self.lineage)
		for k in self.spatial_resolution:
			print '(%s , %s, %s) ' % (k.denominator,k.distance, k.uom)
		for k in self.conformity:
			print '(%s , %s, %s, %s) ' % (k.title,k.date, k.date_type,k.degree)
		print 'Access constraints: %s ' % (self.access_constraints)
		print 'Limitations: %s ' % (self.limitations)
		for k in self.responsible_party:
			print '(%s , %s, %s) ' % (k.organization,k.email, k.role)
