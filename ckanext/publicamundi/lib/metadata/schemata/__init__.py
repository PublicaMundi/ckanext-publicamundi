import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata.ibase import IIntrospective, IObject

# Base interfaces for metadata objects

class IFromConvertedData(zope.interface.Interface):
    
    def from_converted_data(data):
        '''Build object from converter/validator data.

        The term "converted" denotes the format that CKAN user when passes
        data in converters/validators used inside {create/update/read}_package
        IDatasetForm hooks. 
        '''

class IIntrospectiveWithLinkedFields(IIntrospective):
    
    def iter_linked_fields():
        '''Iterate on tuples of (<key-path>, <field>, <parent-field-name>).
        
        The <key-path> part is the path for a field defined in our schema. 
        The <field> part is the unbound Field instance corresponding to the <key-path>.
        The <parent-field-name> part is the name of a field from core CKAN metadata.

        On the definion of a schema, a field can be declared to link to a core field using
        the "links-to" tagged value. E.g.:

        >>> abstract = zope.schema.Text(title=u'Abstract')
        >>> abstact.setTaggedValue('links-to', 'notes')
        '''

class IBaseMetadata(IObject, IFromConvertedData, IIntrospectiveWithLinkedFields):
    
    def deduce_fields(*keys):
        '''Return a dict populated with top-level (not bound to a schema) dataset fields.
        The fields are deduced (if possible) from this object's own fields.
        
        There are 2 basic use cases for the above functionality:
          * import: When importing schema-following metadata (e.g. INSPIRE XML) into 
            the catalog, we need a way to deduce core package fields (e.g. title).
          * edit: When editing metadata, is sometimes desirable to deduce missing fields
            from information present in our schema-bound part.

        If parameter keys is empty, try to deduce every possible field. Otherwise, stick to 
        the keys provided. 
        '''

    def to_extras():
        '''Convert to a map of extras (aka package extras) 
        '''

class IMetadata(IBaseMetadata):

    zope.interface.taggedValue('recurse-on-invariants', False)

    title = zope.schema.TextLine(
        title=u'Title', required=True, min_length=5)    
    title.setTaggedValue('links-to', 'title')

    identifier = zope.schema.NativeStringLine(
        title=u'Identifier', required=True, min_length=3)
    identifier.setTaggedValue('links-to', 'id')

# Import actual interfaces into schemata

from ._common import *
from .ckan_metadata import ICkanMetadata
from .thesaurus import IThesaurus, IThesaurusTerms
from .inspire_metadata import IInspireMetadata
from .foo import IFooMetadata
from .baz import IBazMetadata

