import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

## Define widgets ##

class TextEditFieldWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-text.html'

class TextLineEditFieldWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-textline.html'

class BoolEditFieldWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-bool.html'

class ChoiceEditFieldWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-choice.html'

class TextReadFieldWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-text.html'

class BoolReadFieldWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-bool.html'

class ChoiceReadFieldWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-choice.html'

## Register adapters ##

default_widgets = {
    'read': {
        zope.schema.interfaces.IText: TextReadFieldWidget,
        zope.schema.interfaces.ITextLine: TextReadFieldWidget,
        zope.schema.interfaces.IBytesLine: TextReadFieldWidget,
        zope.schema.interfaces.IBytes: None,
        zope.schema.interfaces.IBool: BoolReadFieldWidget,
        zope.schema.interfaces.IInt: None,
        zope.schema.interfaces.IFloat: None,
        zope.schema.interfaces.IDatetime: None,
        zope.schema.interfaces.IChoice: ChoiceReadFieldWidget,
        zope.schema.interfaces.IDottedName: None,
        zope.schema.interfaces.IURI: None,
    },
    'edit': {
        zope.schema.interfaces.IText: TextEditFieldWidget,
        zope.schema.interfaces.ITextLine: TextLineEditFieldWidget,
        zope.schema.interfaces.IBytesLine: TextLineEditFieldWidget,
        zope.schema.interfaces.IBytes: None,
        zope.schema.interfaces.IBool: BoolEditFieldWidget,
        zope.schema.interfaces.IInt: None,
        zope.schema.interfaces.IFloat: None,
        zope.schema.interfaces.IDatetime: None,
        zope.schema.interfaces.IChoice: ChoiceEditFieldWidget,
        zope.schema.interfaces.IDottedName: None,
        zope.schema.interfaces.IURI: None,
    }
}

for action, widget_mapping in default_widgets.items():
    for field_iface, widget_cls in widget_mapping.items():
        if widget_cls:
            adapter_registry.register([field_iface, None], IFieldWidget, action, widget_cls)

