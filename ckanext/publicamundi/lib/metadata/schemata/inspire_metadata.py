import datetime
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi.lib.metadata import vocabularies
from ckanext.publicamundi.lib.metadata.schemata import IBaseMetadata
from ckanext.publicamundi.lib.metadata.schemata._common import *
from ckanext.publicamundi.lib.metadata.schemata.thesaurus import (
    IThesaurus, IThesaurusTerms)

_ = lambda t:t
keyword_thesaurus_names = filter(
    lambda t: t.startswith('keywords-'), vocabularies.get_names())

class IInspireMetadata(IBaseMetadata):

    zope.interface.taggedValue('recurse-on-invariants', True)

    # Metadata on metadata

    contact = zope.schema.List(
        title = _(u'Metadata Point of Contact'),
        description = _(u'The organisations responsible for the creation and maintenance of the metadata.'),
        required = True,
        min_length = 1,
        max_length = 4,
        value_type = zope.schema.Object(IResponsibleParty,
            title = _(u'Contact'),
            required = True))

    datestamp = zope.schema.Date(
        title = _(u'Metadata Date'),
        description = _(u'The date which specifies when the metadata record was created or updated. This date shall be expressed in conformity with ISO 8601.'),
        required = False,
        defaultFactory = datetime.date.today)

    languagecode = zope.schema.Choice(
        title = _(u'Metadata Language'),
        vocabulary = vocabularies.get_by_name('languages-iso-639-2').get('vocabulary'),
        description = _(u'This is the language in which the metadata elements are expressed. The value domain of this metadata element is limited to the official languages of the Community expressed in conformity with ISO 639-2.'),
        required = True,
        default = 'eng')

    # Identification 
    
    identtype = zope.schema.DottedName(
        title = _(u'Type'),
        required = True,
        default = 'dataset',
    )
    
    title = zope.schema.TextLine(
        title = _(u'Resource Title'),
        description = _(u'This a characteristic (and often unique) name by which the resource is known.'),
        required = True)

    identifier = zope.schema.NativeStringLine(
        title = _(u'Identifier'),
        description = _(u'A value uniquely identifying the dataset. The value domain of this metadata element is a mandatory character string code, generally assigned by the data owner, and a character string namespace uniquely identifying the context of the identifier code (for example, the data owner).'),
        required = True)

    abstract = zope.schema.Text(
        title = _(u'Resource Abstract'),
        description = _(u'This is a brief narrative summary of the contents of this dataset.'),
        required = True)

    locator = zope.schema.List(
        title = _(u'Resource Locator'),
        description = _(u'The resource locator defines the link(s) to the resource and/or the link to additional information about the resource. The value domain of this metadata element is a character string, commonly expressed as uniform resource locator (URL).'),
        required = True,
        min_length = 1,
        max_length = 6,
        value_type = zope.schema.URI(
            title = _(u'Linkage'),
            required = True))

    resource_language = zope.schema.List(
        title = _(u'Resource Languages'),
        description = _(u'The language(s) used within the resource. The value domain of this metadata element is limited to the languages defined in ISO 639-2.'),
        required = False,
        max_length = 5,
        value_type = zope.schema.Choice(
            title = _(u'Resource Language'),
            vocabulary = vocabularies.get_by_name('languages-iso-639-2').get('vocabulary'),))

    # Classification 

    topic_category = zope.schema.List(
        title = _(u'Topic Categories'),
        description = _(u'The topic category is a high-level classification scheme to assist in the grouping and topic-based search of available spatial data resources. The value domain of this metadata element is defined in Part D.2.'),
        required = True,
        min_length = 1,
        max_length = 6,
        value_type = zope.schema.Choice(
            title = _(u'Topic Category'),
            vocabulary = vocabularies.get_by_name('topic-category').get('vocabulary'),))
    topic_category.setTaggedValue('format:markup', { 'descend-if-dictized': False })

    # Keywords

    keywords = zope.schema.Dict(
        title = _(u'Keywords'),
        description = _(u'The keyword value is a commonly used word, formalised word or phrase used to describe the subject. While the topic category is too coarse for detailed queries, keywords help narrowing a full text search and they allow for structured keyword search.'),
        required = True,
        min_length = 1,
        key_type = zope.schema.Choice(
            vocabulary = SimpleVocabulary(
                tuple(SimpleTerm(k, k, vocabularies.get_by_name(k).get('title'))
                    for k in keyword_thesaurus_names)), 
            title = _(u'Keyword Thesaurus')),
        value_type = zope.schema.Object(IThesaurusTerms, 
            title = _(u'Keywords')))
    keywords.setTaggedValue('format:markup', { 'descend-if-dictized': False })

    @zope.interface.invariant
    def check_keywords(obj):
        if obj.keywords:
            if not ('keywords-gemet-inspire-themes' in obj.keywords):
                raise zope.interface.Invalid(
                    _(u'You need to select at least one keyword from INSPIRE data themes'))

    free_keywords = zope.schema.List(
            title= _(u'Free Keywords'),
            description = _(u'The keyword value is a commonly used word, formalised word or phrase used to describe the subject. While the topic category is too coarse for detailed queries, keywords help narrowing a full text search and they allow for structured keyword search.'),
            required = False,
            max_length = 20,
            value_type = zope.schema.Object(IFreeKeyword,
                title = _(u'Free Keyword')))
    free_keywords.setTaggedValue('format:markup', { 'descend-if-dictized': False })

    # Geographic

    bounding_box = zope.schema.List(
        title = _(u'Geographic Bounding Box'),
        description = _(u'This is the extent of the resource in the geographic space, given as a bounding box. The bounding box shall be expressed with westbound and eastbound longitudes, and southbound and northbound latitudes in decimal degrees, with a precision of at least two decimals.'),
        required = True,
        min_length = 1,
        max_length = 4,
        value_type = zope.schema.Object(IGeographicBoundingBox,
            title = _(u'Bounding Box')))
    bounding_box.setTaggedValue('format:markup', { 'descend-if-dictized': True })

    # Temporal 

    temporal_extent = zope.schema.List(
        title = _(u'Temporal Extents'),
        description = _(u'The temporal extent defines the time period covered by the content of the resource. This time period may be expressed as any of the following: - an individual date, - an interval of dates expressed through the starting date and end date of the interval,- a mix of individual dates and intervals of dates.'),
        required = False,
        max_length = 3,
        value_type = zope.schema.Object(ITemporalExtent,
            title = _(u'Extent')))

    creation_date = zope.schema.Date(
        title = _(u'Creation Date'),
        description = _(u'This is the date of creation of the resource. There shall not be more than one date of creation.'),
        required = False)

    publication_date = zope.schema.Date(
        title = _(u'Publication Date'),
        description = _(u'This is the date of publication of the resource when available, or the date of entry into force. There may be more than one date of publication.'),
        required = False)

    revision_date = zope.schema.Date(
        title = _(u'Revision Date'),
        description = _(u'This is the date of last revision of the resource, if the resource has been revised. There shall not be more than one date of last revision.'),
        required = False)

    @zope.interface.invariant
    def check_creation_publication_order(obj):
        errs = []
        
        if obj.creation_date and obj.publication_date:
            if obj.creation_date > obj.publication_date:
                errs.append('Creation date (%s) is later than publication date (%s)' % (
                    obj.creation_date,obj.publication_date))
        
        if obj.publication_date and obj.revision_date:
            if obj.publication_date > obj.revision_date:
                errs.append('Publication date (%s) is later than last revision date (%s)' % (
                    obj.publication_date,obj.revision_date))
        
        if obj.creation_date and obj.revision_date:
            if obj.creation_date > obj.revision_date:
                errs.append('Creation date (%s) is later than last revision date (%s)' % (
                    obj.creation_date,obj.revision_date))

        if errs:
            raise zope.interface.Invalid(errs)

    # Quality & Validity

    lineage = zope.schema.Text(
        title = _(u'Lineage'),
        description = _(u'This is a statement on process history and/or overall quality of the spatial data set. Where appropriate it may include a statement whether the data set has been validated or quality assured, whether it is the official version (if multiple versions exist), and whether it has legal validity. The value domain of this metadata element is free text.'),
        required = False)

    spatial_resolution = zope.schema.List(
        title = _(u'Spatial Resolution'),
        description = _(u'''Spatial resolution refers to the level of detail of the data set. It shall be expressed as a set of zero to many resolution distances (typically for gridded data and imagery-derived products) or equivalent scales (typically for maps or map-derived products). An equivalent scale is generally expressed as an integer value expressing the scale denominator. A resolution distance shall be expressed as a numerical value associated with a unit of length.'''),
        required = False,
        max_length = 6,
        value_type = zope.schema.Object(ISpatialResolution,
            title = _(u'Resolution')))
    spatial_resolution.value_type.setTaggedValue('allow-partial-update', False)

    reference_system = zope.schema.Object(IReferenceSystem,
        title = _(u'Coordinate Reference System'),
        description = _(u'Coordinate Reference System'),
        required = False)
    reference_system.setTaggedValue('format:markup', { 'descend-if-dictized': False })
    
    # Conformity

    conformity = zope.schema.List(
        title = _(u'Conformity'),
        required = False,
        max_length = 4,
        value_type = zope.schema.Object(IConformity,
            title = _(u'Specification')))

    # Constraints 
    
    # Todo: The following fields should have suggestions (autocompleted?) values.

    access_constraints = zope.schema.List(
        title = _(u'Access Constraints'),
        description = _(u'Define the conditions for access and use of spatial data sets and services, and where applicable, corresponding fees as required by Article 5(2)(b) and Article 11(2)(f) of Directive 2007/2/EC. The value domain of this metadata element is free text. The element must have values. If no conditions apply to the access and use of the resource, "no conditions apply" shall be used. If conditions are unknown, "conditions unknown" shall be used. This element shall also provide information on any fees necessary to access and use the resource, if applicable, or refer to a uniform resource locator (URL) where information on fees is available.'),
        required = True,
        min_length = 1,
        max_length = 4,
        value_type = zope.schema.TextLine(title = _(u'Condition')))

    limitations = zope.schema.List(
        title = _(u'Limitations'),
        description = _(u'When member states limit public access to spatial data sets and spatial data services under Article 13 of Directive 2007/2/EC, this metadata element shall provide information on the limitations and the reasons for them. If there are no limitations on public access, this metadata element shall indicate that fact. The value domain of this metadata element is free text.'),
        required = True,
        min_length = 1,
        max_length = 4,
        value_type = zope.schema.TextLine(title = _(u'Limitation')))

    # Responsible Party

    responsible_party = zope.schema.List(
        title = _(u'Responsible Party'),
        description = _(u'The responsible party names the organisation responsible for the establishment, management, maintenance and distribution of resources contained in this dataset.'),
        required = True,
        min_length = 1,
        max_length = 3,
        value_type = zope.schema.Object(IResponsibleParty,
            title = _(u'Party')))

