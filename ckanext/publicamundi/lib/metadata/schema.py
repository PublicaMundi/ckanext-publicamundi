import zope.interface 
import zope.schema
import re
import logging

import ckanext.publicamundi.lib

class IBaseMetadata(zope.interface.Interface):
    
    title = zope.schema.TextLine(
        title = u'Title',
        required = True,
        min_length = 2)
    
    url = zope.schema.URI(
        title = u'URL',
        required = True)

class IContactInfo(zope.interface.Interface):
    
    email = zope.schema.TextLine(
        title = u"Electronic mail address",
        required = True)

    address = zope.schema.Text(
        title = u"Postal address",
        required = True)

    postalCode = zope.schema.TextLine(
        title = u"Postal code",
        constraint = re.compile("\d{5,5}$").match)

class ICkanMetadata(IBaseMetadata):

    @zope.interface.invariant
    def title_is_ok(obj):
        if not len(obj.title) > 1:
            raise ValueError('Title is too short')
 
class IInspireMetadata(IBaseMetadata):
    
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
    
    contacts = zope.schema.List(
        title = u'A list of tags for this bookmark', 
        required = False,
        value_type = zope.schema.Object(IContactInfo,
            title = u'Contact Info'), 
        max_length = 4,
    )

    
    contact_info = zope.schema.Object(
        IContactInfo,
        title = u'Contact Info', 
        required = True)
    

    @zope.interface.invariant
    def title_is_ok(obj):
        if not len(obj.title) > 1:
            raise ValueError('Title is too short')
 

