import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.schemata import IFoo

from ckanext.publicamundi.lib.metadata.types import object_null_adapter
from ckanext.publicamundi.lib.metadata.types import BaseMetadata
from ckanext.publicamundi.lib.metadata.types.common import *

@object_null_adapter(IFoo)
class Foo(BaseMetadata):
    zope.interface.implements(IFoo)

    title = None
    url = None
    thematic_category = None
    tags = list
    baz = None
    contact_info = ContactInfo
    contacts = dict
    geometry = list

