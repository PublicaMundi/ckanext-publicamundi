import zope.interface
import zope.interface.adapter
import zope.schema

adapter_registry = zope.interface.adapter.AdapterRegistry()

# Import basic interfaces

from .ibase import (
    ISerializer, 
    IXmlSerializer,
    IFormatter, 
    IIntrospective,
    IObject)

# Import core functionality: base types, formatters, serializers

from .formatters import (
    field_format_adapter, 
    field_format_multiadapter, 
    formatter_for_field,
    FieldFormatter)

from .serializers import (
    serializer_for_field, 
    serializer_for_key_tuple)

from .base import (
    Object, 
    FieldContext, 
    ErrorDict, 
    object_null_adapter,
    factory_for_object,
    class_for_object,
    object_serialize_adapter,
    serializer_for_object,
    object_format_adapter,
    formatter_for_object,
    ObjectFormatter)

from .xml_serializers import (
    object_xml_serialize_adapter,
    xml_serializer_for_object)

from .schemata import IMetadata

from .types import (
    Metadata,
    deduce,
    dataset_type,
    factory_for_metadata,
    class_for_metadata)

from .i18n import translator_for

# Provide aliases for common functions

factory_for = factory_for_object

class_for = class_for_object

formatter_for = formatter_for_object

serializer_for = serializer_for_object

xml_serializer_for = xml_serializer_for_object

# Import widgets

from .widgets import (
    markup_for_field,
    markup_for_object,
    markup_for,
    widget_for_field,
    widget_for_object)

# Utilities

def iter_dataset_types():
    '''Iterate on all known (i.e. registered) dataset types'''
    for name, cls in adapter_registry.lookupAll([], IMetadata):
        if not name:
            continue # omit unnamed adapters, are meaningless for dataset types
        yield name

def iter_dataset_type_map():
    '''Iterate on all known (i.e. registered) dataset types mapped to a class'''
    for name, cls in adapter_registry.lookupAll([], IMetadata):
        if not name:
            continue # omit unnamed adapters, are meaningless for dataset types
        yield name, cls

def get_dataset_types():
    '''List known dataset types'''
    return set(iter_dataset_types())

def make_metadata(dtype, pkg_dict=None):
    '''Create a metadata object according to the given dataset-type.
    
    If param `pkg_dict` is given, we attempt to load the newly created metadata
    object from a flattened dict with serialized key/values.
    '''
    
    obj = factory_for_metadata(dtype)()
    if pkg_dict:
        opts = {
            'unserialize-keys': True,
            'key-prefix': dtype,
            'unserialize-values': 'default',
        }
        obj.from_dict(pkg_dict, is_flat=True, opts=opts)
    return obj

# Export a (snapshot) of registered dataset types

dataset_types = {}

# Setup (when ready)

def setup():
    '''Gather registered dataset types, cache in exported module-global variable.
    '''

    global dataset_types
    dataset_types = get_dataset_types()

