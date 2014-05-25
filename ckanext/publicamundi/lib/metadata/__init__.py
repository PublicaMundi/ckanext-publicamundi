import zope.interface
import zope.interface.adapter

adapter_registry = zope.interface.adapter.AdapterRegistry()

from ckanext.publicamundi.lib.metadata.schema import IBaseMetadata
from ckanext.publicamundi.lib.metadata.schema import ICkanMetadata, IInspireMetadata
from ckanext.publicamundi.lib.metadata.types import CkanMetadata, InspireMetadata

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

