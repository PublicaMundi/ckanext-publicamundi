import zope.interface 
import zope.schema
import re

from ckanext.publicamundi.lib.metadata.ibase import IBaseObject
from ckanext.publicamundi.lib.metadata.schemata import IBaseMetadata
from ckanext.publicamundi.lib.metadata.schemata.common import *

class ICkanMetadata(IBaseMetadata):
    zope.interface.taggedValue('recurse-on-invariants', True)

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
        default = u'bazinka',
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
 
