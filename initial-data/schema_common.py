import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary
import re
import datetime
import vocabularies 
from helper import *

class IResponsibleParty(zope.interface.Interface):
	organization = zope.schema.TextLine(
		title = u'Organization name',
		required = True,
		min_length = 2)
	email = zope.schema.List(
		title = u'Email',
		required = True,
		min_length = 1,
		value_type = zope.schema.TextLine(
			title = u'Email',
			constraint = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?").match))

	role = zope.schema.Choice(Helper.flatten_dict_vals(vocabularies.party_roles),
		title = u'Responsible party role',
		description = u'This is the role of the responsible organisation.',
		required = True)
	
class IFreeKeyword(zope.interface.Interface):
	value = zope.schema.TextLine(
		title = u"Keyword value",
		description = u"The keyword value is a commonly used word, formalised word or phrase used to describe the subject. While the topic category is too coarse for detailed queries, keywords help narrowing a full text search and they allow for structured keyword search.\nThe value domain of this metadata element is free text.",
		required = False)

	originating_vocabulary = zope.schema.TextLine(
		title = u'Title',
		description = u"If the keyword value originates from a controlled vocabulary (thesaurus, ontology), for example GEMET, the citation of the originating controlled vocabulary shall be provided.\nThis citation shall include at least the title and a reference date (date of publication, date of last revision or of creation) of the originating controlled vocabulary.",
		required = False)
	reference_date = zope.schema.Date(
		title = u'Reference date',
		required = False)
	date_type = zope.schema.Choice(Helper.flatten_dict_vals(vocabularies.date_types),
		title = u'Date Type',
		required = False)
	
	@zope.interface.invariant
    	def check_case_mandatory(obj):
		_mandatory_list.append(obj)
		
		if obj.value or obj.originating_vocabulary or obj.reference_date or obj.date_type:
			if not obj.value or not obj.originating_vocabulary or not obj.reference_date or not obj.date_type:
				raise zope.interface.Invalid('You need to fill in the rest Free Keyword fields')

class IGeographicBoundingBox(zope.interface.Interface):
	nblat = zope.schema.Float(
		title = u'North Bound Latitude',
		min = -90.0,
		max = 90.0,
		required = True)
	sblat = zope.schema.Float(
		title = u'South Bound Latitude',
		min = -90.0,
		max = 90.0,
		required = True)
	eblng = zope.schema.Float(
		title = u'East Bound Longitude',
 		min = -180.0,
		max = 180.0,
		required = True)
	wblng = zope.schema.Float(
		title = u'West Bound Longitude',
		min = -180.0,
		max = 180.0,
		required = True)

_a_greater_b_called = []

class ITemporalExtent(zope.interface.Interface):
	start = zope.schema.Date(
		title = u'Starting date',
		required = False,
		)

	end = zope.schema.Date(
		title = u'Ending date',
		required = False,
		)

	@zope.interface.invariant
    	def check_date_order(obj):
		_a_greater_b_called.append(obj)
		
		if obj.start > obj.end:
			raise zope.interface.Invalid('Start date (%s) later than end date (%s)' % (obj.start,obj.end))


_mandatory_list = []

class ISpatialResolution(zope.interface.Interface):
		
	distance = zope.schema.Int(
		title = u'Resolution distance',
		required = False)

	uom = zope.schema.TextLine(
		title = u'Unit of measure',
		required = False,
		min_length = 2)

	@zope.interface.invariant
    	def check_case_mandatory(obj):
		_mandatory_list.append(obj)
		
		if obj.denominator or obj.distance or obj.uom:
			if not obj.denominator or not obj.distance or not obj.uom:
				raise zope.interface.Invalid('You need to fill in the rest Spatial Resolution fields')

class IConformity(zope.interface.Interface):

	title = zope.schema.TextLine(
		title = u'Specifications',
		required = True)

	date = zope.schema.Date(
		title = u'Date',
		required = True,
		)

	date_type = zope.schema.Choice(Helper.flatten_dict_vals(vocabularies.date_types),
		title = u'Date type',
		required = True)

	degree = zope.schema.Choice(Helper.flatten_dict_vals(vocabularies.degrees),
		title = u'Degree',
		description = u'This is the degree of conformity of the resource to the implementing rules adopted under Article 7(1) of Directive 2007/2/EC or other specification.',
		default = "not_evaluated",
		required = True)
