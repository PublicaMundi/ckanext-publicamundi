import zope.interface

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets.base import (
    EditFieldWidget, EditObjectWidget, 
    ReadFieldWidget, ReadObjectWidget,
    ListFieldWidgetTraits, DictFieldWidgetTraits)

@field_widget_multiadapter([IListField, schemata.IContactInfo],
    qualifiers=['contacts.baz'], is_fallback=True)
class ListOfContactsEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_template(self):
        return 'package/snippets/fields/edit-list-contacts-baz.html'

@object_widget_adapter(schemata.IBaz, qualifiers=['datasetform'], is_fallback=True)
class BazEditWidget(EditObjectWidget):

    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(BazEditWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
    
    def get_field_qualifiers(self):
        return {
            'contacts': 'contacts.baz',
        }
        
    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IBaz)
class BazReadWidget(ReadObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(BazReadWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
   
    def get_field_qualifiers(self):
        return {
            'contacts': 'contacts.baz',
        }

    def get_template(self):
        return None # use glue template

