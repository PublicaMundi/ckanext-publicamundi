import zope.interface

from ckan.plugins import toolkit

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets.base import (
    EditFieldWidget, EditObjectWidget, 
    ReadFieldWidget, ReadObjectWidget,
    ListFieldWidgetTraits, DictFieldWidgetTraits)

_ = toolkit._

@field_widget_multiadapter([IListField, ITextLineField], qualifiers=['tags.foo'])
class TagsEditWidget(EditFieldWidget):

    def __init__(self, field, *args):
        assert isinstance(field, zope.schema.List)
        EditFieldWidget.__init__(self, field)

    def get_template(self):
        return 'package/snippets/fields/edit-list-tags-foo.html'

@field_widget_multiadapter([IListField, ITextLineField], qualifiers=['tags.foo'])
class TagsReadWidget(ReadFieldWidget):

    def __init__(self, field, *args):
        assert isinstance(field, zope.schema.List)
        ReadFieldWidget.__init__(self, field)

    def get_template(self):
        return 'package/snippets/fields/read-list-tags-foo.html'

@field_widget_multiadapter([IDictField, schemata.IContactInfo],
    qualifiers=['contacts.foo'], is_fallback=True)
class DictOfContactsEditWidget(EditFieldWidget, DictFieldWidgetTraits):
 
    def get_template(self):
        return 'package/snippets/fields/edit-dict-contacts-foo.html'

@object_widget_adapter(schemata.IFoo, qualifiers=['datasetform'], is_fallback=True)
class FooEditWidget(EditObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(FooEditWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
   
    def get_field_template_vars(self):
        return {
            'url': {
                'title': _('Web Site'),
            },
        }
    
    def get_field_qualifiers(self):

        qualifiers = super(FooEditWidget, self).get_field_qualifiers()
        qualifiers.pop('geometry') # omit field        
        qualifiers.update({
            'tags': 'tags',
            'thematic_category': 'select2',
            'contacts': 'contacts.foo',
        })
        
        return qualifiers
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-edit-foo-datasetform.html'
        
    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IFoo)
class FooReadWidget(ReadObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(FooReadWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
   
    def get_field_qualifiers(self):
        
        qualifiers = super(FooReadWidget, self).get_field_qualifiers()
        qualifiers['tags'] = 'tags.foo'
        
        return qualifiers
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-foo.html'

    def get_template(self):
        return None # use glue template

