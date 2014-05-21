import zope.interface 
import zope.schema
import re
import logging

import ckanext.publicamundi.lib

class IBaseObject(zope.interface.Interface):
    
    def get_validation_errors():
        '''Invoke all field-level validators and return a dict with errors.'''
    
    def validate_invariants():
        '''Invoke all object-level validators (invariants). 
        On failure, an exception is raised.'''

    def validate():
        '''Validate object (both field-level and object-level).
        Raises an exception on the 1st error encountered.'''

    def to_dict(flatten):
        '''Convert to a (flattened or not) dict'''

class IBaseMetadata(IBaseObject):
    
    title = zope.schema.TextLine(
        title = u'Title',
        required = True,
        min_length = 2)

class IContactInfo(IBaseObject):
    
    email = zope.schema.TextLine(
        title = u"Electronic mail address",
        required = True)

    address = zope.schema.Text(
        title = u"Postal address",
        required = True)

    postalcode = zope.schema.TextLine(
        title = u"Postal code",
        constraint = re.compile("\d{5,5}$").match)

class ICkanMetadata(IBaseMetadata):

    @zope.interface.invariant
    def title_is_ok(obj):
        if not len(obj.title) > 1:
            raise ValueError('Title is too short')
 
class IInspireMetadata(IBaseMetadata):
    
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
    
    contact_info = zope.schema.Object(
        IContactInfo,
        title = u'Contact Info', 
        required = True)
    
    @zope.interface.invariant
    def title_is_ok(obj):
        if not len(obj.title) > 1:
            raise ValueError('Title is too short')
 

