import zope.interface
import zope.interface.adapter
import zope.schema

adapter_registry = zope.interface.adapter.AdapterRegistry()

from ckanext.publicamundi.lib.metadata.ibase import (
    ISerializer, 
    IXmlSerializer, 
    IFormatter, 
    IObject)

from ckanext.publicamundi.lib.metadata.formatters import (
    field_format_adapter, 
    field_format_multiadapter, 
    formatter_for_field)

from ckanext.publicamundi.lib.metadata.serializers import (
    serializer_for_field, 
    serializer_for_key_tuple)

from ckanext.publicamundi.lib.metadata.base import (
    Object, 
    FieldContext, 
    ErrorDict, 
    object_null_adapter,
    get_object_factory,
    object_serialize_adapter,
    serializer_for_object,
    object_format_adapter,
    formatter_for_object,
    ObjectFormatter)

from ckanext.publicamundi.lib.metadata.xml_serializers import (
    object_xml_serialize_adapter,
    xml_serializer_for_object)

from ckanext.publicamundi.lib.metadata.widgets import (
    markup_for_field,
    markup_for_object,
    markup_for,
    widget_for_field,
    widget_for_object)

# Aliases for common functions

formatter_for = formatter_for_object

serializer_for = serializer_for_object

xml_serializer_for = xml_serializer_for_object

# Import common schemata/types

from ckanext.publicamundi.lib.metadata.schemata import (
    IFoo, IBaz, ICkanMetadata, IInspireMetadata)

from ckanext.publicamundi.lib.metadata.types import (
    Foo, Baz, CkanMetadata, InspireMetadata)

# Declare dataset types (i.e. metadata formats).

# Note If, for a certain dataset-type, a "class" value is not given,
# then a suitable class will be lookup-up in the adapter registry.

dataset_types = {
    'ckan': {
        'title': 'CKAN',
        'description': u'Provide core CKAN metadata',
        'schema': ICkanMetadata,
        'class': CkanMetadata,
    },
    'inspire': {
        'title': 'INSPIRE',
        'description': u'Provide metadata according to the INSPIRE EU directive',
        'schema': IInspireMetadata,
        'class': InspireMetadata,
        'key_prefix': 'inspire', 
    },
    'foo': {
        'title': 'Foo',
        'description': u'Provide metadata according to an arbitrary "foo" schema',
        'schema': IFoo,
        'class': Foo,
        'key_prefix': 'foo', 
    },
    'baz': { 
        'title': 'Baz',
        'description': u'Provide metadata according to an arbitrary "baz" schema',
        'schema': IBaz,
        'class': Baz,
        'key_prefix': 'baz', 
    },
}

def make_object(t):
    assert t in dataset_types
    factory = dataset_types[t]['class']
    obj = factory()
    return obj

