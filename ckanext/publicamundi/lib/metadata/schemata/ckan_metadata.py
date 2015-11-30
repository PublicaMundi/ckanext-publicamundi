import zope.interface
import zope.schema
import re

from ckanext.publicamundi.lib.metadata.ibase import IObject

from . import IMetadata

class ICkanMetadata(IMetadata):
    
    zope.interface.taggedValue('recurse-on-invariants', True)

