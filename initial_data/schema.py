import zope.interface
import zope.schema
import re
import datetime
import vocabularies 

class IPointOfContact(zope.interface.Interface):
	organization_name = zope.schema.TextLine(
		title = u"Organization Name",
		description = u"The name of the organization",
		required = True)
	email = zope.schema.List(
		title = u"Email",
		required = True,
		min_length = 1,
		value_type = zope.schema.TextLine(
			title = u'Email',
			constraint = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?").match))

class IInspireMetadata(zope.interface.Interface): 
     
	point_of_contact = zope.schema.List(
		title = u'Metadata Point of Contact',
		description = u"This is the description of the organisation responsible for the creation and maintenance of the metadata. This description shall include:   - the name of the organisation as free text, - a contact e-mail address as a character string.",
		required = True,
		min_length = 1,
		value_type = zope.schema.Object(IPointOfContact, 
			title = u'A Point of Contact',
			required = True))
	
	metadata_date = zope.schema.Date(
		title = u'Metadata Date',
		description = u"The date which specifies when the metadata record was created or updated. This date shall be expressed in conformity with ISO 8601.",
		required = False,
		default = datetime.date.today(),
		max = datetime.date.today())
	
	metadata_language = zope.schema.Choice(vocabularies.languages,
		title = u'Metadata Language',
		description = u"This is the language in which the metadata elements are expressed.The value domain of this metadata element is limited to the official languages of the Community expressed in conformity with ISO 639-2.",
		required = True,
		default = "English")

class IIdentifier(zope.interface.Interface):
	code = zope.schema.TextLine(
		title = u"Code",
		required = True)

	codespace = zope.schema.DottedName(
		title = u"Codespace",
		required = False)

class IInspireIdentification(zope.interface.Interface):
	
	resource_title = zope.schema.TextLine(
		title = u'Resource Title',
		description = u"This a characteristic, and often unique, name by which the resource is known.                                                       The value domain of this metadata element is free text.",
		required = True)

	identifier = zope.schema.List(
		title = u'Identifier',
		description = u"A value uniquely identifying the resource.                                                The value domain of this metadata element is a mandatory character string code, generally assigned by the data owner, and a character string namespace uniquely identifying the context of the identifier code (for example, the data owner).",
		required = True,
		min_length = 1,
		value_type = zope.schema.Object(IIdentifier, title = u'Identifier'))
        
	resource_abstract = zope.schema.Text(
		title = u"Resource Abstract",
		description = u"This is a brief narrative summary of the content of the resource. The value domain of this metadata element is free text.",
		required = True)

	resource_locator = zope.schema.List(
		title = u'Resource locator',
		description = u"The resource locator defines the link(s) to the resource and/or the link to additional information about the resource. The value domain of this metadata element is a character string, commonly expressed as uniform resource locator (URL).",
		required = True,
		min_length = 1,
		value_type = zope.schema.URI(
			title = u'Linkage',
			required = True))

	resource_language = zope.schema.List(
		title = u'Resource Language',
		description = u"The language(s) used within the resource. The value domain of this metadata element is limited to the languages defined in ISO 639-2.",
		required = False,
		value_type = zope.schema.Choice(vocabularies.languages))

class IInspireClassification(zope.interface.Interface):
	
	topic_category = zope.schema.Choice(vocabularies.topic_category,
	title = u'Topic Category',
	description = u"The topic category is a high-level classification scheme to assist in the grouping and topic-based search of available spatial data resources. The value domain of this metadata element is defined in Part D.2.",
	required = True
    )

class IGeographicBoundingBox(zope.interface.Interface):
	north_bound_latitude = zope.schema.Float(
		title = u'North Bound Latitude',
		min = -90.0,
		max = 90.0,
		required = True)
	south_bound_latitude = zope.schema.Float(
		title = u'South Bound Latitude',
		min = -90.0,
		max = 90.0,
		required = True)
	east_bound_longitude = zope.schema.Float(
		title = u'East Bound Longitude',
 		min = -180.0,
		max = 180.0,
		required = True)
	west_bound_longitude = zope.schema.Float(
		title = u'West Bound Longitude',
		min = -180.0,
		max = 180.0,
		required = True)


class IInspireGeographic(zope.interface.Interface):

	geographic_bounding_box = zope.schema.List( 
		title = u'Geographic Bounding Box', 
		description = u"This is the extent of the resource in the geographic space, given as a bounding box. The bounding box shall be expressed with westbound and eastbound longitudes, and southbound and northbound latitudes in decimal degrees, with a precision of at least two decimals.",
		required = True,
		min_length = 1,
		value_type = zope.schema.Object(IGeographicBoundingBox, 
			title = u'Geographic Bounding Box'))

	geographic_countries = zope.schema.Choice(vocabularies.countries,
            title = u'Countries',
            required = False)

_a_greater_b_called = []
class ITemporalExtent(zope.interface.Interface):
	starting_date = zope.schema.Date(
		title = u'Starting date',
		required = False,
		max = datetime.date.today())

	ending_date = zope.schema.Date(
		title = u'Ending date',
		required = False,
		max = datetime.date.today())

	@zope.interface.invariant
    	def check_date_order(obj):
		_a_greater_b_called.append(obj)
		if obj.starting_date > obj.ending_date:
			raise zope.interface.Invalid('Start date (%s) later than end date (%s)' % (obj.starting_date,obj.ending_date))
	

class IInspireTemporal(zope.interface.Interface):
	
	temporal_extent = zope.schema.List(
		title = u'Temporal Extent',
		description = u"The temporal extent defines the time period covered by the content of the resource. This time period may be expressed as any of the following: - an individual date, - an interval of dates expressed through the starting date and end date of the interval,- a mix of individual dates and intervals of dates.",
		required = False,
		value_type = zope.schema.Object(ITemporalExtent,
			title = u'Temporal extent'))
	creation_date = zope.schema.Date(
		title = u'Date of creation',
		description = u"This is the date of creation of the resource. There shall not be more than one date of creation.",
		required = False,
		max = datetime.date.today())
	publication_date = zope.schema.Date(
		title = u'Date of publication',
		description = u"This is the date of publication of the resource when available, or the date of entry into force. There may be more than one date of publication.",
		required = False,
		max = datetime.date.today())
	revision_date = zope.schema.Date(
		title = u'Date of last revision',
		description = u"This is the date of last revision of the resource, if the resource has been revised. There shall not be more than one date of last revision.",
		required = False,
		max = datetime.date.today())
	
	@zope.interface.invariant
	def check_creation_publication_order(obj):
		_a_greater_b_called.append(obj)
		if obj.creation_date > obj.publication_date:
			raise zope.interface.Invalid('Creation date (%s) later than publication date (%s)' % (obj.creation_date,obj.publication_date))

	@zope.interface.invariant
	def check_publication_revision_order(obj):
		_a_greater_b_called.append(obj)
		if obj.publication_date > obj.revision_date:
			raise zope.interface.Invalid('Publication date (%s) later than last revision date (%s)' % (obj.publication_date,obj.revision_date))


class ISpatialResolution(zope.interface.Interface):
	equivalent_scale = zope.schema.Int(
		title = u'Equivalent Scale',
		required = False)
	resolution_distance = zope.schema.Int(
		title = u'Resolution distance',
		required = False)
	unit_of_measure = zope.schema.TextLine(
		title = u'Unit of measure',
		required = False)
#TODO what invariants for spatial resolution?

class IInspireQualityValidity(zope.interface.Interface):
	
	lineage = zope.schema.Text(
		title = u'Lineage',
		description = u"This is a statement on process history and/or overall quality of the spatial data set. Where appropriate it may include a statement whether the data set has been validated or quality assured, whether it is the official version (if multiple versions exist), and whether it has legal validity. The value domain of this metadata element is free text.",
		required = False)
	spatial_resolution = zope.schema.List(
		title = u'Spatial resolution',
		description = u"Spatial resolution refers to the level of detail of the data set. It shall be expressed as a set of zero to many resolution distances (typically for gridded data and imagery-derived products) or equivalent scales (typically for maps or map-derived products). An equivalent scale is generally expressed as an integer value expressing the scale denominator. A resolution distance shall be expressed as a numerical value associated with a unit of length.",
		required = False,
		value_type = zope.schema.Object(ISpatialResolution,
			title = u'Spatial resolution'))

class IConformity(zope.interface.Interface):
	#specifications have suggestions vocabulary!
	specifications = zope.schema.TextLine(
		title = u'Specifications',
		description = u"This is a citation of the implementing rules adopted under Article 7(1) of Directive 2007/2/EC or other specification to which a particular resource conforms. A resource may conform to more than one implementing rules adopted under Article 7(1) of Directive 2007/2/EC or other specification. This citation shall include at least the title and a reference date (date of publication, date of last revision or of creation) of the implementing rules adopted under Article 7(1) of Directive 2007/2/EC or of the specification.",
		required = False)
	date = zope.schema.Date(
		title = u'Date',
		required = True,
		max = datetime.date.today())
	date_type = zope.schema.Choice(vocabularies.date_type,
		title = u'Date type',
		required = True)
	degree = zope.schema.Choice(vocabularies.degree,
		title = u'Degree',
		description = u"This is the degree of conformity of the resource to the implementing rules adopted under Article 7(1) of Directive 2007/2/EC or other specification.",
		required = True)

class IInspireConformity(zope.interface.Interface):
	conformity = zope.schema.List(
		title = u'Conformity',
		required = False,
		value_type = zope.schema.Object(IConformity,
			title = u'Conformity'))

class IInspireConstraints(zope.interface.Interface):
	#conditions have suggestions vocabulary
	conditions = zope.schema.List(
		title = u'Conditions applying to access and use',
		description = u'This metadata element defines the conditions for access and use of spatial data sets and services, and where applicable, corresponding fees as required by Article 5(2)(b) and Article 11(2)(f) of Directive 2007/2/EC. The value domain of this metadata element is free text. \nThe element must have values. If no conditions apply to the access and use of the resource, "no conditions apply" shall be used. If conditions are unknown, "conditions unknown" shall be used. This element shall also provide information on any fees necessary to access and use the resource, if applicable, or refer to a uniform resource locator (URL) where information on fees is available.',
		required = True,
		min_length = 1,
		value_type = zope.schema.TextLine(title = u'Condition'))
	# limitations have suggestsions vocabulary 
	limitations = zope.schema.List(
		title = u'Limitations on public access',
		description = u"When Member States limit public access to spatial data sets and spatial data services under Article 13 of Directive 2007/2/EC, this metadata element shall provide information on the limitations and the reasons for them. If there are no limitations on public access, this metadata element shall indicate that fact.\nThe value domain of this metadata element is free text.",
		required = True,
		min_length = 1,
		value_type = zope.schema.TextLine(title = u'Limitation'))

class IResponsibleParty(zope.interface.Interface):
	point_of_contact = zope.schema.Object(IPointOfContact,
		title = u'Responsible Party',
		required = True)
	party_role = zope.schema.Choice(vocabularies.party_roles,
		title = u'Responsible party role',
		description = u'This is the role of the responsible organisation.',
		required = True)

class IInspireResponsibleParty(zope.interface.Interface):
	responsible_party = zope.schema.List(
		title = u'Responsible Party',
		description = u'This is the description of the organisation responsible for the establishment, management, maintenance and distribution of the resource.\nThis description shall include:\n- the name of the organisation as free text,\n- a contact e-mail address as a character string.',
		required = True,
		min_length = 1,
		value_type = zope.schema.Object(IResponsibleParty,
			title = u'Responsible Party'))

class IOriginatingVocabulary(zope.interface.Interface):
	title = zope.schema.TextLine(
		title = u'Title',
		required = True)
	reference_date = zope.schema.Date(
		title = u'Reference date',
		required = True)
	date_type = zope.schema.Choice(vocabularies.date_type,
		title = u'Date Type',
		required = True)

class IFreeKeyword(zope.interface.Interface):
	keyword_value = zope.schema.TextLine(
		title = u"Keyword value",
		description = u"The keyword value is a commonly used word, formalised word or phrase used to describe the subject. While the topic category is too coarse for detailed queries, keywords help narrowing a full text search and they allow for structured keyword search.\nThe value domain of this metadata element is free text.",
		required = True)
	originating_vocabulary = zope.schema.Object(IOriginatingVocabulary,
		title = u'Originating controlled vocabulary',
		description = u"If the keyword value originates from a controlled vocabulary (thesaurus, ontology), for example GEMET, the citation of the originating controlled vocabulary shall be provided.\nThis citation shall include at least the title and a reference date (date of publication, date of last revision or of creation) of the originating controlled vocabulary.",
		required = True)
	
inspire_data_themes_items = []

_mandatory_list = []
class IInspireKeyword(zope.interface.Interface):

	
	free_keyword = zope.schema.Object(IFreeKeyword,
		title = u'Free keyword',
		required = True)

	keywords = zope.schema.List(
		title = u'Keyword value',
		description = u'The keyword value is a commonly used word, formalised word or phrase used to describe the subject. While the topic category is too coarse for detailed queries, keywords help narrowing a full text search and they allow for structured keyword search.',
		required = True,
		min_length = 1,
		value_type = zope.schema.Dict(
			key_type = zope.schema.Choice(vocabularies.vocabularies.keys()),
			value_type = zope.schema.List(
				required = True,
				min_length = 1)
))

	@zope.interface.invariant
    	def check_mandatory(obj):
		_mandatory_list.append(obj)
		for item in vocabularies.vocabularies.get('inspire_data_themes'):
			inspire_data_themes_items.append(item.get('value'))
		check = False
		for k in obj.keywords:
			if 'inspire_data_themes' in k.keys():
				check = True
		if not check:
			raise zope.interface.Invalid('You need to select at least one keyword from INSPIRE data theme')
			
				
	
	
		

		
