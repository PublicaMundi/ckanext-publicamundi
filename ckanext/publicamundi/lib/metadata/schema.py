import zope.interface 
import zope.schema
import re

import ckanext.publicamundi.lib
from ckanext.publicamundi.lib.metadata.ibase import IBaseObject

class IBaseMetadata(IBaseObject):

    zope.interface.taggedValue('recurse-on-invariants', False)

    title = zope.schema.TextLine(
        title = u'Title',
        required = True,
        min_length = 2)

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
        max_length = 10, 
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

class ICkanMetadata(IBaseMetadata):

    @zope.interface.invariant
    def title_is_ok(obj):
        if not len(obj.title) > 1:
            raise ValueError('Title is too short')

class IInspireMetadata(IBaseMetadata):
    
    zope.interface.taggedValue('recurse-on-invariants', True)
    
    url = zope.schema.URI(
        title = u'URL',
        required = True)
   
    thematic_category = zope.schema.Choice(('environment', 'government', 'health'), 
        title = u'The main thematic category',
        required = False,
        default = 'government')

    baz = zope.schema.TextLine(
        title = u'Baz', 
        required = False,
        min_length = 5)

    tags = zope.schema.List(
        title = u'A list of tags for this bookmark', 
        required = False,
        value_type = zope.schema.TextLine(
            title = u'Tag', 
            constraint = re.compile('[-a-z0-9]+$').match),
        max_length = 5,
    )
    
    geometry = zope.schema.List(
        title = u'A collection of areas', 
        required = False,
        value_type = zope.schema.List(
            title = u'A polygon area', 
            value_type = zope.schema.Object(IPolygon,
                title = u'A polygon'
            ),
            max_length = 2),
        max_length = 2,
    )
   
    contacts = zope.schema.Dict(
        title = u'A list of contacts', 
        required = False,
        key_type = zope.schema.Choice(('personal', 'office'),
            title = u'The type of contact'),
        value_type = zope.schema.Object(IContactInfo, 
            title = u'Contact'),
    )
   
    contact_info = zope.schema.Object(IContactInfo,
        title = u'Contact Info', 
        required = True)
    
    @zope.interface.invariant
    def check_tag_duplicates(obj):
        s = set(obj.tags)
        if len(s) < len(obj.tags):
            raise zope.interface.Invalid('Tags contain duplicates')
 
