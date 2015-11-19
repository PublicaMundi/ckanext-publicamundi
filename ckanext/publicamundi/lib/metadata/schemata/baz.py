import re
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi.lib.metadata.ibase import IObject

from . import IMetadata
from ._common import *
from .thesaurus import IThesaurusTerms

class IBazMetadata(IMetadata):
    
    zope.interface.taggedValue('recurse-on-invariants', True)

    url = zope.schema.URI(
        title = u'URL',
        required = True)

    contacts = zope.schema.List(
        title = u'Contacts',
        required = False,
        min_length = 1,
        max_length = 5,
        value_type = zope.schema.Object(IContactInfo,
            title = u'Contact',
            required = True))
    
    keywords = zope.schema.Object(IThesaurusTerms,
        title = u'Baz Keywords',
        required = False)

    bbox = zope.schema.Object(IGeographicBoundingBox,
        title = u'Baz BBox',
        required = True)

    resolution = zope.schema.Object(ISpatialResolution,
        title = u'Spatial Resolution',
        required = False)
