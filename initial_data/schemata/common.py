from ckanext.publicamundi.lib.metadata.ibase import IBaseObject
import zope.interface 
import zope.schema
import re
import datetime
import initial_data.helper as h

class IPostalAddress(IBaseObject):
    
    address = zope.schema.Text(
        title = u"Postal address",
        required = True)

    postalcode = zope.schema.TextLine(
        title = u"Postal code",
        required = True,
        constraint = re.compile("\d{5,5}$").match)
   
class IPoint(IBaseObject):
     
    x = zope.schema.Float() 
    y = zope.schema.Float()  

class IPolygon(IBaseObject):
    
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

class IContactInfo(IBaseObject):
    
    email = zope.schema.TextLine(title=u"Electronic mail address", required=False)
    
    address = zope.schema.Object(IPostalAddress, title=u"Postal Address", required=False)

    @zope.interface.invariant
    def not_empty(obj):
        if obj.email is None and obj.address is None:
            raise zope.interface.Invalid('At least one of email/address should be supplied')

class ITemporalExtent(IBaseObject):

    start = zope.schema.Datetime(
        title = u'Starting date',
        required = False,
        max = datetime.datetime.now())

    end = zope.schema.Datetime(
        title = u'Ending date',
        required = False)

    @zope.interface.invariant
    def check_date_order(obj):
        if obj.start > obj.end:
            msg = 'The start-date (%s) is later than end-date (%s)' % (obj.start,obj.end)
            raise zope.interface.Invalid(msg)


class IResponsibleParty(IBaseObject):
	organization = zope.schema.TextLine(
		title = u'Organization name',
		required = True,
		min_length = 2)

	email = zope.schema.List(
		title = u'Email',
		required = True,
		min_length = 1,
		value_type = zope.schema.TextLine(
			constraint = re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?").match))

	role = zope.schema.Choice(h.get_terms('party_roles'),
		title = u'Responsible party role',
		description = u'This is the role of the responsible organisation.',
		required = True)

class IGeographicBoundingBox(IBaseObject):
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


class ISpatialResolution(IBaseObject):
		
	distance = zope.schema.Int(
		title = u'Resolution distance',
		required = False)

	uom = zope.schema.TextLine(
		title = u'Unit of measure',
		required = False,
		min_length = 2)

	@zope.interface.invariant
    	def check_case_mandatory(obj):
		#_mandatory_list.append(obj)
		
		if obj.denominator or obj.distance or obj.uom:
			if not obj.denominator or not obj.distance or not obj.uom:
				raise zope.interface.Invalid('You need to fill in the rest Spatial Resolution fields')

class IConformity(IBaseObject):

	title = zope.schema.TextLine(
		title = u'Specifications',
		required = True)

	date = zope.schema.Date(
		title = u'Date',
		required = True)
		#max = datetime.date.today())

	date_type = zope.schema.Choice(h.get_terms('date_types'),
		title = u'Date type',
		required = True)

	degree = zope.schema.Choice(h.get_terms('degrees'),
		title = u'Degree',
		description = u'This is the degree of conformity of the resource to the implementing rules adopted under Article 7(1) of Directive 2007/2/EC or other specification.',
		default = "not_evaluated",
		required = True)

