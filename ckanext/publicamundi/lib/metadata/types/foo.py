import zope.interface

from ckanext.publicamundi.lib.metadata.base import (
    Object, object_null_adapter,
    object_format_adapter, ObjectFormatter)
from ckanext.publicamundi.lib.metadata import xml_serializers 
from ckanext.publicamundi.lib.metadata.schemata import IFoo

from . import Metadata
from . import deduce
from ._common import *

@object_null_adapter()
class Foo(Metadata):

    zope.interface.implements(IFoo)

    ## Factories for fields ## 

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
    description = None
    temporal_extent = None
    reviewed = None
    created = None
    published = None
    password = None
    wakeup_time = None

    ## Deduce methods ##

    @deduce('url', 'id')
    def _deduce_ids(self): 
        return dict(url=self.url, id=self.url)

    @deduce('notes')
    def _deduce_notes(self): 
        return self.description
    

@xml_serializers.object_xml_serialize_adapter(IFoo)
class FooXmlSerializer(xml_serializers.ObjectSerializer):
    pass

@object_format_adapter(IFoo)
class FooFormatter(ObjectFormatter):
    pass
