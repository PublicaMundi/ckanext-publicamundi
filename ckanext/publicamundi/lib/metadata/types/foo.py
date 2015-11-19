import zope.interface

from ckanext.publicamundi.lib.metadata.base import (
    Object, object_null_adapter,
    object_format_adapter, ObjectFormatter)
from ckanext.publicamundi.lib.metadata import xml_serializers 
from ckanext.publicamundi.lib.metadata.schemata import IFooMetadata

from . import Metadata, deduce, dataset_type
from ._common import *

@dataset_type('foo')
@object_null_adapter()
class FooMetadata(Metadata):

    zope.interface.implements(IFooMetadata)

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

    @deduce('url')
    def _deduce_url(self): 
        return self.url

    @deduce('notes')
    def _deduce_notes(self): 
        return self.description
    
    @deduce('id')
    def _deduce_id(self): 
        return self.identifier

@xml_serializers.object_xml_serialize_adapter(IFooMetadata)
class FooXmlSerializer(xml_serializers.ObjectSerializer):
    pass

@object_format_adapter(IFooMetadata)
class FooFormatter(ObjectFormatter):
    pass
