import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata import IBaz

from ckanext.publicamundi.lib.metadata.types import BaseMetadata

@object_null_adapter()
class Baz(BaseMetadata):

    zope.interface.implements(IBaz)

    url = None
    contacts = list
    keywords = None
