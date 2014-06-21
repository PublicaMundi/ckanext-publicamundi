import zope.interface
import zope.interface.adapter
import zope.schema

adapter_registry = zope.interface.adapter.AdapterRegistry()

from ckanext.publicamundi.lib.metadata.ibase import ISerializer, IObject
from ckanext.publicamundi.lib.metadata.base import Object, FieldContext
from ckanext.publicamundi.lib.metadata.schemata import ICkanMetadata, IInspireMetadata
from ckanext.publicamundi.lib.metadata.types import CkanMetadata, InspireMetadata
from ckanext.publicamundi.lib.metadata.widgets import markup_for_field, markup_for_object

dataset_types = {
    'ckan': {
        'title': 'CKAN',
        'cls': CkanMetadata,
    },
    'inspire': {
        'title': 'INSPIRE',
        'cls': InspireMetadata,
    },
    'fgdc': {
        'title': 'FGDC',
        'cls': None,
    },
}

