import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata.ibase import IObject

class IBaseMetadata(IObject):
    zope.interface.taggedValue('recurse-on-invariants', False)

    title = zope.schema.TextLine(
        title = u'Title',
        required = True, 
        min_length = 5)

from ckanext.publicamundi.lib.metadata.schemata._common import *
from ckanext.publicamundi.lib.metadata.schemata.ckan_metadata import ICkanMetadata
from ckanext.publicamundi.lib.metadata.schemata.inspire_metadata import \
    IThesaurus, IThesaurusTerms, IInspireMetadata
from ckanext.publicamundi.lib.metadata.schemata.foo import IFoo

