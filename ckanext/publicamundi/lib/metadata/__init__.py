
import ckanext.publicamundi.lib

from ckanext.publicamundi.lib.metadata.schema import ICkanMetadata, IInspireMetadata
from ckanext.publicamundi.lib.metadata.types import CkanMetadata, InspireMetadata

dataset_types = {
    'ckan': { 
        'title': 'CKAN',
        'class': CkanMetadata,
    },
    'inspire': {
        'title': 'INSPIRE',
        'class': InspireMetadata,
    },
    'fgdc': {
        'title': 'FGDC',
        'class': None,
    },
}

