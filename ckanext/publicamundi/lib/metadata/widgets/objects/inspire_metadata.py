import zope.interface
from collections import OrderedDict

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets.base import (
    EditFieldWidget, EditObjectWidget, 
    ReadFieldWidget, ReadObjectWidget,
    ListFieldWidgetTraits, DictFieldWidgetTraits)

@object_widget_adapter(schemata.IInspireMetadata, 
    qualifiers=['datasetform'], is_fallback=True)
class InspireEditWidget(EditObjectWidget):

    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(InspireEditWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars

    def get_field_qualifiers(self):
        return OrderedDict([
            ('languagecode', 'select2'),
            ('datestamp', None),
        ])
        
    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IInspireMetadata)
class InspireReadWidget(ReadObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(InspireReadWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
     
    def get_field_qualifiers(self):
        return OrderedDict([
            ('languagecode', None),
            ('datestamp', None),
        ])

    def get_template(self):
        return None # use glue template

