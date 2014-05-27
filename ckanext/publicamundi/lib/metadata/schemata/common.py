import zope.interface 
import zope.schema
import re
import datetime

from ckanext.publicamundi.lib.metadata.ibase import IBaseObject

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


