from collections import OrderedDict

import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.metadata.widgets import object_widget_adapter
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.widgets.base import (
    EditObjectWidget, ReadObjectWidget)

@object_widget_adapter(schemata.ICkanMetadata, 
    qualifiers=['datasetform'], is_fallback=True)
class EditWidget(EditObjectWidget):
    
    def get_field_qualifiers(self):
        return OrderedDict([])
    
    def get_template(self):
        return None # use glue template

