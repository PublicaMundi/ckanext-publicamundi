import zope.schema
import re
import datetime

import vocabularies.py

import ckanext.publicamundi.lib 
from ckanext.publicamundi.lib.metadata.ibase import IBaseObject 


class IPointΟfContact(IBaseObject):
    organizationName = zope.schema.TextLine(
        title = u"Organisation Name",
        required = True)
        
    email = zope.schema.TextLine(
        title = u"E-mail",
        required = True,
        constraint = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?").match)

class IIdentifier(IBaseObject):
    code = zope.schema.Id(
        title = u"Code",
        required = True)

    codespace = zope.schema.DottedName(
        title = u"Codespace",
        required = False)

class IGeographicBoundingBox(IBaseObject):
    northBoundLatitude = zope.schema.Float(
        title = u'North Bound Latitude',
        min = -90,
        max = 90,
        required = True)
    southhBoundLatitude = zope.schema.Float(
        title = u'South Bound Latitude',
        min = -90,
        max = 90,
        required = True)
    eastBoundLongitude = zope.schema.Float(
        title = u'East Bound Longitude',
        min = -180,
        max = 180,
        required = True)
    westBoundLongitude = zope.schema.Float(
        title = u'West Bound Longitude',
        min = -180,
        max = 180,
        required = True)

class IInspireMetadata(IBaseMetadata): 
     
    zope.interface.taggedValue('recurse-on-invariants', True) 
    
    metadataPointOfContact = zope.schema.List(
        title = u'Metadata Point of Contact',
        description = u"This is the description of the organisation responsible for the creation and maintenance of the metadata. This description shall include:   - the name of the organisation as free text, - a contact e-mail address as a character string.",
        required = True,
        value_type = zope.schema.Object(IPointΟfContact,
            title = u'A Point of Contact'),
    )
        
    metadataDate = zope.schema.Date(
        title = u'Metadata Date',
        description = u"The date which specifies when the metadata record was created or updated. This date shall be expressed in conformity with ISO 8601.",
        required = False,
        default = datetime.date.today(),
        max = datetime.date.today()
    )
        
    metadataLanguage = zope.schema.Choice(SimpleVocabulary.fromValues(vocabularies.languages),
        title = u'Metadata Language',
        description = u"This is the language in which the metadata elements are expressed.The value domain of this metadata element is limited to the official languages of the Community expressed in conformity with ISO 639-2.",
        required = True,
        default = "English")
        
    identificationResourceTitle = zope.schema.TextLine(
        title = u'Resource Title',
        description = u"This a characteristic, and often unique, name by which the resource is known.                                                       The value domain of this metadata element is free text.",
        required = True)

    identificationIdentifier = zope.schema.List(
        title = u'Identifier',
        description = u"A value uniquely identifying the resource.                                                The value domain of this metadata element is a mandatory character string code, generally assigned by the data owner, and a character string namespace uniquely identifying the context of the identifier code (for example, the data owner).",
        required = True,
        value_type = zope.schema.Object(IIdentifier, title = u'Identifier'),
    )
        
    identificationResourceAbstract = zope.schema.Text(
        title = u"Resource Abstract",
        description = u"This is a brief narrative summary of the content of the resource. The value domain of this metadata element is free text.",
        required = True,
        )
    identificationResourceLocator = zope.schema.List(
        title = u'Resource locator',
        description = u"The resource locator defines the link(s) to the resource and/or the link to additional information about the resource. The value domain of this metadata element is a character string, commonly expressed as uniform resource locator (URL).",
        required = True,
        value_type = zope.schema.URI(
            title = u'Linkage',
            required = True)
        )
    identificationResourceLanguage = zope.schema.List(
        title = u'Resource Language',
        description = u"The language(s) used within the resource. The value domain of this metadata element is limited to the languages defined in ISO 639-2.",
        required = False,
        value_type = zope.schema.Choice(SimpleVocabulary.fromValues(vocabularies.languages))
    )
    
    classificationTopicCategory = zope.schema.Choice(SimpleVocabulary.fromValues(vocabularies.topic_category),
        title = u'Topic Category',
        description = u"The topic category is a high-level classification scheme to assist in the grouping and topic-based search of available spatial data resources. The value domain of this metadata element is defined in Part D.2.",
        required = True
    )
    
    geographicBoundingBox = zope.schema.Object(IGeographicBoundingBox, title = u'Geographic Bounding Box', description = u"This is the extent of the resource in the geographic space, given as a bounding box. The bounding box shall be expressed with westbound and eastbound longitudes, and southbound and northbound latitudes in decimal degrees, with a precision of at least two decimals.")
    geographicCountries = zope.schema.Choice(SimpleVocabulary.fromValues(vocabularies.countries),
            title = u'Countries',
            required = False)
    
 }