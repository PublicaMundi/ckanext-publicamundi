import zope.interface
import zope.schema
import re
import datetime
from common import *
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from ckanext.publicamundi.lib.metadata.helpers import vocabularies
from ckanext.publicamundi.lib.metadata.helpers import keywords
from ckanext.publicamundi.lib.metadata.ibase import IObject

class IThesaurus(IObject):

    title = zope.schema.TextLine(
        title = u"Title",
        required = True)

    reference_date = zope.schema.Date(
        title = u"Date",
        required = True)

    date_type = zope.schema.Choice(Helper.flatten_dict_vals(vocabularies.date_types),
        title = u"Date Type",
        required = True)

    name = zope.schema.Choice(vocabulary = SimpleVocabulary((
            SimpleTerm('gemet_concepts', 'gemet_concepts', u'GEMET Concepts'),
            SimpleTerm('inspire_feature_concept_dictionary', 'inspire_feature_concept_dictionary', u'Inspire Feature Concept Dictionary'),
            SimpleTerm('gemet_supergroups', 'gemet_supergroups', u'GEMET Supergroups'),
            SimpleTerm('gemet_groups', 'gemet_groups', u'GEMET Groups'),
            SimpleTerm('inspire_data_themes', 'inspire_data_themes', u'INSPIRE Data Themes'),
            SimpleTerm('geoss_societal_benefit_areas', 'geoss_societal_benefit_areas', u'GEOSS Societal Benefit'),
            SimpleTerm('inspire_glossary', 'inspire_glossary', u'INSPIRE Glossary'),
            SimpleTerm('geoss_earth_observation_vocabulary', 'geoss_earth_observation_vocabulary', u'GEOSS Earth Observation Vocabulary'),
            SimpleTerm('gemet_themes', 'gemet_themes', u'GEMET Themes'))),

        title = u"Machine friendly name",
        required = True)

    terms = zope.schema.List(
        title = u"Terms",
        value_type = zope.schema.ASCII(),
        #zope.schema.Choice(Helper.get_all_keyword_terms()),
        required = True,
        min_length = 1)

class IInspireMetadata(IObject):
    zope.interface.taggedValue('recurse-on-invariants', True)
    #Metadata on metadata

    contact = zope.schema.List(
        title = u'Metadata Point of Contact',
        description = u"This is the description of the organisation responsible for the creation and maintenance of the metadata. This description shall include:   - the name of the organisation as free text, - a contact e-mail address as a character string.",
        required = True,
        min_length = 1,
        value_type = zope.schema.Object(IResponsibleParty,
            title = u'A Point of Contact',
            required = True))

    datestamp = zope.schema.Date(
        title = u'Metadata Date',
        description = u"The date which specifies when the metadata record was created or updated. This date shall be expressed in conformity with ISO 8601.",
        required = False,
        default = datetime.date.today())

    languagecode = zope.schema.Choice(Helper.flatten_dict_vals(vocabularies.languages),
        title = u'Metadata Language',
        description = u"This is the language in which the metadata elements are expressed.The value domain of this metadata element is limited to the official languages of the Community expressed in conformity with ISO 639-2.",
        required = True,
        default = "en")

    #Identification 

    title = zope.schema.TextLine(
        title = u'Resource Title',
        description = u"This a characteristic, and often unique, name by which the resource is known.                                                       The value domain of this metadata element is free text.",
        required = True)

    ## TODO: What constraints are needed for identifier??

    identifier = zope.schema.List(
        title = u'Identifier',
        description = u"A value uniquely identifying the resource. The value domain of this metadata element is a mandatory character string code, generally assigned by the data owner, and a character string namespace uniquely identifying the context of the identifier code (for example, the data owner).",
        required = True,
        min_length = 1,
        value_type = zope.schema.TextLine(title = u'Identifier',
            min_length = 5 ))

    abstract = zope.schema.Text(
        title = u"Resource Abstract",
        description = u"This is a brief narrative summary of the content of the resource. The value domain of this metadata element is free text.",
        required = True)

    locator = zope.schema.List(
        title = u'Resource locator',
        description = u"The resource locator defines the link(s) to the resource and/or the link to additional information about the resource. The value domain of this metadata element is a character string, commonly expressed as uniform resource locator (URL).",
        required = True,
        min_length = 1,
        #min_length = 2,
        #max_length = 3,
        value_type = zope.schema.URI(
            title = u'Linkage',
            required = True))

    resource_language = zope.schema.List(
        title = u'Resource Language',
        description = u"The language(s) used within the resource. The value domain of this metadata element is limited to the languages defined in ISO 639-2.",
        required = False,
        value_type = zope.schema.Choice(Helper.flatten_dict_vals(vocabularies.languages)))
    ## TODO: identtype, textline, choice?? 

    #Classification 

    topic_category = zope.schema.List(
        title = u'Topic Category',
        description = u"The topic category is a high-level classification scheme to assist in the grouping and topic-based search of available spatial data resources. The value domain of this metadata element is defined in Part D.2.",
        required = True,
        min_length = 1,
        value_type = zope.schema.Choice(Helper.flatten_dict_vals(vocabularies.topic_category)))
    #Keywords

    keywords = zope.schema.List(
        title = u'Keyword value',
        description = u'The keyword value is a commonly used word, formalised word or phrase used to describe the subject. While the topic category is too coarse for detailed queries, keywords help narrowing a full text search and they allow for structured keyword search.',
        required = True,
        min_length = 1,
        value_type = zope.schema.Object(IThesaurus))

    @zope.interface.invariant
    def check_mandatory(obj):
        found = False
        #print 'obj ', obj.keywords
        for k in obj.keywords:
            #for k in obj:
            obj_dict = k.to_dict()
            if 'name' in obj_dict:
                if obj_dict.get('name') == 'inspire_data_themes':
                    found = True
        if not found:
            raise zope.interface.Invalid('You need to select at least one keyword from INSPIRE data themes')

    @zope.interface.invariant
    def check_relative_value_type(obj):
        errors = []
        for k in obj.keywords:
            obj_dict = k.to_dict()
            #print 'obj ', obj_dict
            allowed_keywords = Helper.flatten_dict_vals(Helper.get_keyword_dict(obj_dict.get('name')).get('terms'))
            for key in obj_dict.get('terms'):
                if not key in allowed_keywords:
                    errors.append('Keyword %s does not belong to thesaurus %s' % (key, obj_dict.get('title')))
        if errors:
            raise zope.interface.Invalid(errors)

    #Geographic
    bounding_box = zope.schema.List(title = u'Geographic Bounding Box',
    description = u"This is the extent of the resource in the geographic space, given as a bounding box. The bounding box shall be expressed with westbound and eastbound longitudes, and southbound and northbound latitudes in decimal degrees, with a precision of at least two decimals.",
    required = True,
    min_length = 1,
    value_type = zope.schema.Object(IGeographicBoundingBox,
        title = u'Geographic Bounding Box'))

    # Temporal 

    temporal_extent = zope.schema.List(
        title = u'Temporal Extent',
        description = u"The temporal extent defines the time period covered by the content of the resource. This time period may be expressed as any of the following: - an individual date, - an interval of dates expressed through the starting date and end date of the interval,- a mix of individual dates and intervals of dates.",
        required = False,
        value_type = zope.schema.Object(ITemporalExtent,
            title = u'Temporal extent'))

    creation_date = zope.schema.Date(
        title = u'Date of creation',
        description = u"This is the date of creation of the resource. There shall not be more than one date of creation.",
        required = False)

    publication_date = zope.schema.Date(
        title = u'Date of publication',
        description = u"This is the date of publication of the resource when available, or the date of entry into force. There may be more than one date of publication.",
        required = False)

    revision_date = zope.schema.Date(
        title = u'Date of last revision',
        description = u"This is the date of last revision of the resource, if the resource has been revised. There shall not be more than one date of last revision.",
        required = False)

    @zope.interface.invariant
    def check_creation_publication_order(obj):
        err_list = []
        if obj.creation_date > obj.publication_date:
            err_list.append('Creation date (%s) later than publication date (%s)' % (obj.creation_date,obj.publication_date))
            #zope.interface.Invalid('Creation date later than publication date')
        if obj.publication_date > obj.revision_date:
            err_list.append('Publication date (%s) later than last revision date (%s)' % (obj.publication_date,obj.revision_date))
        if err_list:
            raise zope.interface.Invalid(err_list)

            #raise zope.interface.Invalid('Creation date (%s) later than publication date (%s)' % (obj.creation_date,obj.publication_date))

    #@zope.interface.invariant
    #def check_publication_revision_order(obj):
    #    if obj.publication_date > obj.revision_date:
    #        raise zope.interface.Invalid('Publication date (%s) later than last revision date (%s)' % (obj.publication_date,obj.revision_date))

    # Quality & Validity

    lineage = zope.schema.Text(
        title = u'Lineage',
        description = u"This is a statement on process history and/or overall quality of the spatial data set. Where appropriate it may include a statement whether the data set has been validated or quality assured, whether it is the official version (if multiple versions exist), and whether it has legal validity. The value domain of this metadata element is free text.",
        required = False)

    denominator = zope.schema.List(
        title = u'Equivalent scale',
        required = False,
        value_type = zope.schema.Int())

    spatial_resolution = zope.schema.List(
        title = u'Spatial resolution',
        description = u"Spatial resolution refers to the level of detail of the data set. It shall be expressed as a set of zero to many resolution distances (typically for gridded data and imagery-derived products) or equivalent scales (typically for maps or map-derived products). An equivalent scale is generally expressed as an integer value expressing the scale denominator. A resolution distance shall be expressed as a numerical value associated with a unit of length.",
        required = False,
        value_type = zope.schema.Object(ISpatialResolution,
            title = u'Spatial resolution'))

    # Conformity

    conformity = zope.schema.List(
        title = u'Conformity',
        required = False,
        value_type = zope.schema.Object(IConformity,
            title = u'Conformity'))

    #Constraints 
    ## TODO xreiazomaste other_constraints??

    access_constraints = zope.schema.List(
        title = u'Conditions applying to access and use',
        description = u'This metadata element defines the conditions for access and use of spatial data sets and services, and where applicable, corresponding fees as required by Article 5(2)(b) and Article 11(2)(f) of Directive 2007/2/EC. The value domain of this metadata element is free text. \nThe element must have values. If no conditions apply to the access and use of the resource, "no conditions apply" shall be used. If conditions are unknown, "conditions unknown" shall be used. This element shall also provide information on any fees necessary to access and use the resource, if applicable, or refer to a uniform resource locator (URL) where information on fees is available.',
        required = True,
        min_length = 1,
        value_type = zope.schema.TextLine(title = u'Condition'))

    limitations = zope.schema.List(
        title = u'Limitations on public access',
        description = u"When Member States limit public access to spatial data sets and spatial data services under Article 13 of Directive 2007/2/EC, this metadata element shall provide information on the limitations and the reasons for them. If there are no limitations on public access, this metadata element shall indicate that fact.\nThe value domain of this metadata element is free text.",
        required = True,
        min_length = 1,
        value_type = zope.schema.TextLine(title = u'Limitation'))

    #Responsible Party

    responsible_party = zope.schema.List(
        title = u'Responsible Party',
        description = u'This is the description of the organisation responsible for the establishment, management, maintenance and distribution of the resource.\nThis description shall include:\n- the name of the organisation as free text,\n- a contact e-mail address as a character string.',
        required = True,
        min_length = 1,
        value_type = zope.schema.Object(IResponsibleParty,
            title = u'Responsible Party'))
