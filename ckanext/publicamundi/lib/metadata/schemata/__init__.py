import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata.ibase import IObject

# Base interface for metadata objects

class IBaseMetadata(IObject):
    
    zope.interface.taggedValue('recurse-on-invariants', False)

    title = zope.schema.TextLine(
        title = u'Title',
        required = True, 
        min_length = 5)
    
    def deduce_basic_fields():
        '''Return a dict populated with basic (i.e. core) package fields.
        These fields are deduced (if possible) from this object's own fields.
        '''

# Import actual interfaces into schemata

from ckanext.publicamundi.lib.metadata.schemata._common import *
from ckanext.publicamundi.lib.metadata.schemata.ckan_metadata import ICkanMetadata
from ckanext.publicamundi.lib.metadata.schemata.thesaurus import IThesaurus, IThesaurusTerms
from ckanext.publicamundi.lib.metadata.schemata.inspire_metadata import IInspireMetadata
from ckanext.publicamundi.lib.metadata.schemata.foo import IFoo
from ckanext.publicamundi.lib.metadata.schemata.baz import IBaz

