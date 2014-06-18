import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata.ibase import IObject

class IBaseMetadata(IObject):
    zope.interface.taggedValue('recurse-on-invariants', False)

    title = zope.schema.TextLine(title=u'Title', required=True, min_length=5)

from ckanext.publicamundi.lib.metadata.schemata.common import *
from ckanext.publicamundi.lib.metadata.schemata.metadata import ICkanMetadata
from ckanext.publicamundi.lib.metadata.schemata.metadata import IInspireMetadata

