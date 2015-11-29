import zope.interface

from ckanext.publicamundi.lib.metadata.base import Object, object_null_adapter
from ckanext.publicamundi.lib.metadata import xml_serializers 
from ckanext.publicamundi.lib.metadata.schemata import ICkanMetadata

from . import Metadata, dataset_type

@dataset_type('ckan')
@object_null_adapter()
class CkanMetadata(Metadata):
    
    zope.interface.implements(ICkanMetadata)

    title = None

@xml_serializers.object_xml_serialize_adapter(ICkanMetadata)
class CkanXmlSerializer(xml_serializers.ObjectSerializer):
    pass

