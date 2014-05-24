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
		print 'Point Of Contact( organization, email):'
		for k in self.point_of_contact:
			print '(%s , %s) ' % (k.organization_name,k.email)
		print 'Date: %s ' % (self.metadata_date)
		print 'Language: %s ' % (self.metadata_language)
