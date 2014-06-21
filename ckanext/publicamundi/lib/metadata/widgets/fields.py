import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

## Define widgets ##

class TextEditWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-text.html'

class TextLineEditWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-textline.html'

class BoolEditWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-checkbox-1.html'

class ChoiceEditWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-choice.html'

class TextReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-text.html'

class BoolReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-bool.html'

class ChoiceReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-choice.html'

## Register adapters ##

def register_field_widget(field_iface, widget_cls):
    adapter_registry.register(
        [field_iface], IFieldWidget, widget_cls.action, widget_cls)

default_widgets = [
    # Readers
    (zope.schema.interfaces.IText, TextReadWidget),
    (zope.schema.interfaces.ITextLine, TextReadWidget),
    (zope.schema.interfaces.IBytesLine, TextReadWidget),
    (zope.schema.interfaces.IBytes, None),
    (zope.schema.interfaces.IBool, BoolReadWidget),
    (zope.schema.interfaces.IInt, None),
    (zope.schema.interfaces.IFloat, None),
    (zope.schema.interfaces.IDatetime, None),
    (zope.schema.interfaces.IChoice, ChoiceReadWidget),
    (zope.schema.interfaces.IDottedName, None),
    (zope.schema.interfaces.IURI, None),
    # Editors
    (zope.schema.interfaces.IText, TextEditWidget),
    (zope.schema.interfaces.ITextLine, TextLineEditWidget),
    (zope.schema.interfaces.IBytesLine, TextLineEditWidget),
    (zope.schema.interfaces.IBytes, None),
    (zope.schema.interfaces.IBool, BoolEditWidget),
    (zope.schema.interfaces.IInt, None),
    (zope.schema.interfaces.IFloat, None),
    (zope.schema.interfaces.IDatetime, None),
    (zope.schema.interfaces.IChoice, ChoiceEditWidget),
    (zope.schema.interfaces.IDottedName, None),
    (zope.schema.interfaces.IURI, None),
]

for field_iface, widget_cls in default_widgets:
    if widget_cls:
        register_field_widget(field_iface, widget_cls)

