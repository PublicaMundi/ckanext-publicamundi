import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

## Define widgets ##

class TextEditFieldWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-text.html'

class TextReadFieldWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-text.html'

## Register adapters ##

default_widgets = {
    'read': {
        zope.schema.interfaces.IText: TextReadFieldWidget,
        zope.schema.interfaces.ITextLine: TextReadFieldWidget,
    },
    'edit': {
        zope.schema.interfaces.IText: TextEditFieldWidget,
        zope.schema.interfaces.ITextLine: TextEditFieldWidget,
    }
}

for action, widget_mapping in default_widgets.items():
    for field_iface, widget_cls in widget_mapping.items():
        adapter_registry.register([field_iface, None], IFieldWidget, action, widget_cls)

