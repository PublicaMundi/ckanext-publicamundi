import zope.interface 
import zope.schema
import logging

import ckanext.publicamundi.lib

class ICkanMetadata(zope.interface.Interface):

    title = zope.schema.TextLine(
        title = u'Title',
        required = True)

    url = zope.schema.URI(
        title = u'URL',
        required = True)

    @zope.interface.invariant
    def title_is_ok(obj):
        if not len(obj.title) > 1:
            raise ValueError('Title is too short')
 

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

    baz = zope.schema.TextLine(
        title = u'Baz', 
        required = False,
        min_length = 5)

    @zope.interface.invariant
    def title_is_ok(obj):
        if not len(obj.title) > 1:
            raise ValueError('Title is too short')
 

