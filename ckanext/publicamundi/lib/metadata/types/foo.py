import zope.interface

from ckanext.publicamundi.lib.metadata.base import (
    Object, object_null_adapter,
    object_format_adapter, ObjectFormatter)
from ckanext.publicamundi.lib.metadata.schemata import IFoo
from ckanext.publicamundi.lib.metadata.types import BaseMetadata
from ckanext.publicamundi.lib.metadata.types._common import *
from ckanext.publicamundi.lib.metadata import xml_serializers 

@object_null_adapter()
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
    rating = None
    grade = None
    notes = None
    temporal_extent = None
    reviewed = None
    created = None
    published = None
    password = None
    wakeup_time = None

@xml_serializers.object_xml_serialize_adapter(IFoo)
class FooXmlSerializer(xml_serializers.ObjectSerializer):
    pass

@object_format_adapter(IFoo, 'default')
class FooFormatter(ObjectFormatter):
    pass
