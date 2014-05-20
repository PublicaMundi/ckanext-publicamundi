import zope.interface 
import zope.schema

import logging

class IInspireMetadata(zope.interface.Interface):

    title = zope.schema.TextLine(
        title = u'Title',
        required = True)

    url = zope.schema.URI(
        title = u'URL',
        required = True)
    
    thematic_category = zope.schema.Choice(('environment', 'government', 'health'), 
        title = u'The main thematic category',
        required = False,
        default = 'government')

    @zope.interface.invariant
    def title_is_ok(obj):
        if not len(obj.title) > 1:
            raise ValueError('Title is too short')
 

