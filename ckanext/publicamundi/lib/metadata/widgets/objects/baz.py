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

@field_widget_multiadapter([IListField, schemata.IContactInfo],
    qualifiers=['contacts.baz'], is_fallback=True)
class ListOfContactsEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_template(self):
        return 'package/snippets/fields/edit-list-contacts-baz.html'

@object_widget_adapter(schemata.IBaz, qualifiers=['datasetform'], is_fallback=True)
class BazEditWidget(EditObjectWidget):
    
    def get_field_template_vars(self):
        return {
            'keywords': {
                'classes': ['control-group']
            }
        }
    
    def get_field_qualifiers(self):
        return OrderedDict([
            ('url', None),
            ('contacts', 'contacts.baz'),
            ('keywords', 'select2'),
            ('bbox', None),
        ])
        
    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IBaz)
class BazReadWidget(ReadObjectWidget):
   
    def get_field_qualifiers(self):
        return OrderedDict([
            ('url', None),
            ('contacts', 'contacts.baz'),
        ])

    def get_template(self):
        return None # use glue template

