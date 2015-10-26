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
    
    def deduce_fields(keys=()):
        '''Return a dict populated with top-level (not bound to a schema) dataset fields.
        The fields are deduced (if possible) from this object's own fields.
        
        There are 2 basic use cases for the above functionality:
          * import: When importing schema-following metadata (e.g. INSPIRE XML) into 
            the catalog, we need a way to deduce core package fields (e.g. title).
          * edit: When editing metadata, is sometimes desirable to deduce missing fields
            from information present in our schema-following part.

        If parameter keys is empty, try to deduce every possible field. Otherwise, stick to 
        the keys provided. 
        '''

# Import actual interfaces into schemata

from ._common import *
from .ckan_metadata import ICkanMetadata
from .thesaurus import IThesaurus, IThesaurusTerms
from .inspire_metadata import IInspireMetadata
from .foo import IFoo
from .baz import IBaz

