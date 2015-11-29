from collections import OrderedDict

from ckanext.publicamundi.lib.metadata.widgets import object_widget_adapter
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

@object_widget_adapter(schemata.ICkanMetadata, 
    qualifiers=['datasetform'], is_fallback=True)
class EditWidget(base_widgets.EditObjectWidget):
    
    def get_field_qualifiers(self):
        return OrderedDict([])
    
    def get_template(self):
        return None # use glue template

