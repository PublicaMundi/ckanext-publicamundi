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
	email = zope.schema.TextLine(
		title = u"Email",
		required = True,
		constraint = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?").match)

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

	geographic_bounding_box = zope.schema.Object(IGeographicBoundingBox, 
		title = u'Geographic Bounding Box', 
		description = u"This is the extent of the resource in the geographic space, given as a bounding box. The bounding box shall be expressed with westbound and eastbound longitudes, and southbound and northbound latitudes in decimal degrees, with a precision of at least two decimals.")

	geographic_countries = zope.schema.Choice(vocabularies.countries,
            title = u'Countries',
            required = False)
