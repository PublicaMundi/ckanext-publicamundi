import re
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata.schemata import IBaseMetadata
from ckanext.publicamundi.lib.metadata.schemata._common import *
from ckanext.publicamundi.lib.metadata.schemata.thesaurus import IThesaurusTerms

class IBaz(IBaseMetadata):
    
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

