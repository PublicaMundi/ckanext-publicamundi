import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata.schemata.ckan_metadata import ICkanMetadata
from ckanext.publicamundi.lib.metadata.types import BaseMetadata
from ckanext.publicamundi.lib.metadata import xml_serializers 

@object_null_adapter()
class CkanMetadata(BaseMetadata):
    
    zope.interface.implements(ICkanMetadata)

    title = None

@xml_serializers.object_xml_serialize_adapter(ICkanMetadata)
class CkanXmlSerializer(xml_serializers.ObjectSerializer):
    pass

