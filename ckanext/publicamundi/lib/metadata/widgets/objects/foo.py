import zope.interface

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.widgets import object_widget_adapter
from ckanext.publicamundi.lib.metadata.widgets import field_widget_adapter
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

@object_widget_adapter(schemata.IFoo)
class FooEditWidget(base_widgets.EditObjectWidget):

    def prepare_template_vars(self, name_prefix, data):
        data = base_widgets.EditObjectWidget.prepare_template_vars(self, name_prefix, data)
        # Add variables
        return data
    
    def get_omitted_fields(self):
        return ['geometry']
    
    def get_field_qualifiers(self):
        return {
            'tags': 'tags.foo',
            'contacts': 'contacts.foo',
        }
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-edit-foo.html'
        
    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IFoo)
class FooReadWidget(base_widgets.ReadObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        data = base_widgets.ReadObjectWidget.prepare_template_vars(self, name_prefix, data)
        # Add variables
        return data
    
    def get_omitted_fields(self):
        return ['geometry']
   
    def get_field_qualifiers(self):
        return {
        }
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-foo.html'

    def get_template(self):
        return None # use glue template

