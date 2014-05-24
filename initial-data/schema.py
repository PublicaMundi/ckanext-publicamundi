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
