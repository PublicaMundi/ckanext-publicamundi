import re
import datetime
import zope.interface
import zope.schema
import zope.schema.vocabulary
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import z3c.schema.email

from ckanext.publicamundi.lib.metadata import vocabularies
from ckanext.publicamundi.lib.metadata.ibase import IObject

class IPostalAddress(IObject):

    address = zope.schema.Text(
        title = u"Postal address",
        required = True)

    postalcode = zope.schema.TextLine(
        title = u"Postal code",
        required = True,
        constraint = re.compile("\d{5,5}$").match)

class IPoint(IObject):

    x = zope.schema.Float(required=True)
    y = zope.schema.Float(required=True)

class IPolygon(IObject):

    points = zope.schema.List(
        title = u'Points',
        value_type = zope.schema.Object(IPoint, title=u'Point'),
        required = True,
        max_length = 8,
        min_length = 4)

    name = zope.schema.TextLine()

    @zope.interface.invariant
    def check_polygon(obj):
        if not (obj.points[0] == obj.points[-1]):
            raise zope.interface.Invalid('The polygon line must be closed')

class IContactInfo(IObject):

    email = z3c.schema.email.RFC822MailAddress(title=u'Email',
        description=u'Electronic mail address', required=False)

    address = zope.schema.Object(IPostalAddress, title=u"Postal Address", required=False)
    
    publish = zope.schema.Bool(title=u'Publish', 
        description=u'This information can be safely published', required=False)

    @zope.interface.invariant
    def not_empty(obj):
        if obj.email is None and obj.address is None:
            raise zope.interface.Invalid('At least one of email/address should be supplied')

class IResponsibleParty(IObject):

    organization = zope.schema.TextLine(
        title = u'Organization Name',
        required = True,
        min_length = 2)

    email = z3c.schema.email.RFC822MailAddress(
        title = u'Email',
        required = True)

    role = zope.schema.Choice(
        title = u'Responsible Party Role',
        vocabulary = vocabularies.get_by_name('party-roles').get('vocabulary'), 
        description = u'This is the role of the responsible organisation.',
        default = 'pointofcontact',
        required = True)

class IFreeKeyword(IObject):

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

    date_type = zope.schema.Choice(
        title = u'Date Type',
        vocabulary = vocabularies.get_by_name('date-types').get('vocabulary'),
        required = False)

    @zope.interface.invariant
    def check_mandatory_parts(obj):
        if obj.value or obj.originating_vocabulary or obj.reference_date or obj.date_type:
            if not obj.value or not obj.originating_vocabulary or not obj.reference_date or not obj.date_type:
                raise zope.interface.Invalid('You need to fill in the rest free-keyword fields')

class IGeographicBoundingBox(IObject):
    
    sblat = zope.schema.Float(
        title = u'South Bound Latitude',
        min = -90.0,
        max = 90.0,
        default = .0,
        required = True)

    nblat = zope.schema.Float(
        title = u'North Bound Latitude',
        min = -90.0,
        max = 90.0,
        default = .0,
        required = True)
    
    wblng = zope.schema.Float(
        title = u'West Bound Longitude',
        min = -180.0,
        max = 180.0,
        default = .0,
        required = True)

    eblng = zope.schema.Float(
        title = u'East Bound Longitude',
        min = -180.0,
        max = 180.0,
        default = .0,
        required = True)

    @zope.interface.invariant
    def check_wb_eb(obj):
        if (obj.wblng > obj.eblng):
            raise zope.interface.Invalid(
                'The east bound must be greater than the west bound')
    
    @zope.interface.invariant
    def check_sb_nb(obj):
        if (obj.sblat > obj.nblat):
            raise zope.interface.Invalid(
                'The north bound must be greater than the south bound')

class ITemporalExtent(IObject):

    start = zope.schema.Date(
        title = u'Start Date',
        required = True,)

    end = zope.schema.Date(
        title = u'End Date',
        required = True,)

    @zope.interface.invariant
    def check_date_order(obj):
        if obj.start > obj.end:
            msg = 'The start-date (%s) is later than end-date (%s)' % (obj.start, obj.end)
            raise zope.interface.Invalid(msg)

class ISpatialResolution(IObject):
    
    denominator = zope.schema.Int(
        title = u'Equivalent Scale',
        min = 1, # positive integer
        required = False)

    distance = zope.schema.Int(
        title = u'Resolution Distance',
        min = 1, # positive integer
        required = False)

    uom = zope.schema.TextLine(
        title = u'Unit of Measure',
        required = False,
        min_length = 2)

    @zope.interface.invariant
    def check(obj):
        # A valid spatial-resolution must have at least one of the following:
        # (i) a denominator, or (ii) a distance with a specified unit
        if not obj.denominator:
            if not (obj.distance and obj.uom):
                raise zope.interface.Invalid(
                    'At least of one of (i) a denominator, or (ii) a distance must be given.')

class IConformity(IObject):

    title = zope.schema.TextLine(
        title = u'Specification',
        required = True)

    date = zope.schema.Date(
        title = u'Date',
        required = True)

    date_type = zope.schema.Choice(
        title = u'Date Type',
        vocabulary = vocabularies.get_by_name('date-types').get('vocabulary'),
        required = True)

    degree = zope.schema.Choice(
        title = u'Degree',
        vocabulary = vocabularies.get_by_name('degrees').get('vocabulary'),
        description = u'This is the degree of conformity of the resource to the implementing rules adopted under Article 7(1) of Directive 2007/2/EC or other specification.',
        default = "not-evaluated",
        required = True)
