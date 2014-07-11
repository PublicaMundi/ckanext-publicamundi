import zope.interface
import zope.schema
import z3c.schema.email
import re
import datetime

from ckanext.publicamundi.lib.metadata.helpers import vocabularies
from ckanext.publicamundi.lib.metadata.helpers.helper import *
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

    x = zope.schema.Float()
    y = zope.schema.Float()

class IPolygon(IObject):

    points = zope.schema.List(
        value_type = zope.schema.Object(IPoint),
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

    @zope.interface.invariant
    def not_empty(obj):
        if obj.email is None and obj.address is None:
            raise zope.interface.Invalid('At least one of email/address should be supplied')

class IResponsibleParty(IObject):

    organization = zope.schema.TextLine(
        title = u'Organization name',
        required = True,
        min_length = 1)

    email = zope.schema.List(
        title = u'Email',
        required = True,
        min_length = 1,
        value_type = z3c.schema.email.RFC822MailAddress(
            title = u'Email'))

    role = zope.schema.Choice(Helper.flatten_dict_vals(Helper.get_vocabulary_terms('party_roles')),
        title = u'Responsible party role',
        description = u'This is the role of the responsible organisation.',
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

    date_type = zope.schema.Choice(Helper.flatten_dict_vals(Helper.get_vocabulary_terms('date_types')),
        title = u'Date Type',
        required = False)

    @zope.interface.invariant
    def check_case_mandatory(obj):
        if obj.value or obj.originating_vocabulary or obj.reference_date or obj.date_type:
            if not obj.value or not obj.originating_vocabulary or not obj.reference_date or not obj.date_type:
                raise zope.interface.Invalid('You need to fill in the rest Free Keyword fields')

class IGeographicBoundingBox(IObject):

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

class ITemporalExtent(IObject):

    start = zope.schema.Date(
        title = u'Starting date',
        required = True,)

    end = zope.schema.Date(
        title = u'Ending date',
        required = True,)

    @zope.interface.invariant
    def check_date_order(obj):
        if obj.start > obj.end:
            msg = 'The start date (%s) is later than end date (%s)' % (obj.start,obj.end)
            raise zope.interface.Invalid(msg)

class ISpatialResolution(IObject):

    distance = zope.schema.Int(
        title = u'Resolution distance',
        required = True)

    uom = zope.schema.TextLine(
        title = u'Unit of measure',
        required = True,
        min_length = 2)

    '''
    @zope.interface.invariant
    def check_case_mandatory(obj):
        if obj.distance or obj.uom:
            if not obj.distance or not obj.uom:
                raise zope.interface.Invalid('You need to fill in the rest Spatial Resolution fields')
    '''

class IConformity(IObject):

    title = zope.schema.TextLine(
        title = u'Specifications',
        required = True)

    date = zope.schema.Date(
        title = u'Date',
        required = True,
        )

    date_type = zope.schema.Choice(Helper.flatten_dict_vals(Helper.get_vocabulary_terms('date_types')),
        title = u'Date type',
        required = True)

    degree = zope.schema.Choice(Helper.flatten_dict_vals(Helper.get_vocabulary_terms('degrees')),
        title = u'Degree',
        description = u'This is the degree of conformity of the resource to the implementing rules adopted under Article 7(1) of Directive 2007/2/EC or other specification.',
        #default = u"not_evaluated",
        required = True)
