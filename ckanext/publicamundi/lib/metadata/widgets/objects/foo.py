import zope.interface

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import object_widget_adapter
from ckanext.publicamundi.lib.metadata.widgets import field_widget_adapter
from ckanext.publicamundi.lib.metadata.widgets import field_widget_multiadapter
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

@field_widget_multiadapter([IListField, ITextLineField], qualifiers=['tags.foo'])
class TagsEditWidget(base_widgets.EditFieldWidget, base_widgets.ListFieldWidgetTraits):

    def __init__(self, field, *args):
        assert isinstance(field, zope.schema.List)
        base_widgets.EditFieldWidget.__init__(self, field)

    def get_template(self):
        return 'package/snippets/fields/edit-list-tags-foo.html'

@field_widget_multiadapter([IListField, ITextLineField], qualifiers=['tags.foo'])
class TagsReadWidget(base_widgets.ReadFieldWidget, base_widgets.ListFieldWidgetTraits):

    def __init__(self, field, *args):
        assert isinstance(field, zope.schema.List)
        base_widgets.ReadFieldWidget.__init__(self, field)

    def get_template(self):
        return 'package/snippets/fields/read-list-tags-foo.html'

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
            'tags': 'tags',
            'thematic_category': 'select2',
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
            'tags': 'tags.foo',
        }
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-foo.html'

    def get_template(self):
        return None # use glue template

