import zope.interface
import zope.schema

from ckan.plugins import toolkit

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import Object, FieldContext
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import logger

## Define widgets ##

# Editors #

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

class ListEditWidget(base_widgets.EditFieldWidget, base_widgets.ListWidgetTraits):

    def __init__(self, field, qualified_action):
        assert \
            isinstance(field, zope.schema.List) or \
            isinstance(field, zope.schema.Tuple)
        base_widgets.EditFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/edit-list.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.ListWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'list'),
            ]),
        })
        return data

class DictEditWidget(base_widgets.EditFieldWidget, base_widgets.DictWidgetTraits):

    def __init__(self, field, qualified_action):
        assert isinstance(field, zope.schema.Dict)
        base_widgets.EditFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/edit-dict.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.DictWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'dict'),
            ]),
        })
        return data

# Readers #

class TextReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-text.html'

class TextAsItemReadWidget(base_widgets.ReadFieldWidget):

    qualifiers = ['item']

    def get_template(self):
        return 'package/snippets/fields/read-text-item.html'

class BoolReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-bool.html'

class ChoiceReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-choice.html'

class ListReadWidget(base_widgets.ReadFieldWidget, base_widgets.ListWidgetTraits):

    def __init__(self, field, qualified_action):
        assert \
            isinstance(field, zope.schema.List) or \
            isinstance(field, zope.schema.Tuple)
        base_widgets.ReadFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/read-list.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.ListWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'list'),
            ]),
        })
        return data

class DictReadWidget(base_widgets.ReadFieldWidget, base_widgets.DictWidgetTraits):

    def __init__(self, field, qualified_action):
        assert isinstance(field, zope.schema.Dict)
        base_widgets.ReadFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/read-dict.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.DictWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'dict'),
            ]),
        })
        return data

## Register adapters ##

def register_field_widget(field_iface, widget_cls):
    for name in widget_cls.get_qualified_actions():
        adapter_registry.register(
            [field_iface, None], IFieldWidget, name, widget_cls)
        logger.info('Registered adapter %s for field [%s, None] with name "%s"', 
            widget_cls.__name__, field_iface.__name__, name)

default_widgets = [
    # Readers
    (zope.schema.interfaces.IText, TextReadWidget),
    (zope.schema.interfaces.ITextLine, TextReadWidget),
    (zope.schema.interfaces.ITextLine, TextAsItemReadWidget),
    (zope.schema.interfaces.IBytesLine, TextReadWidget),
    (zope.schema.interfaces.IBytes, None),
    (zope.schema.interfaces.IBool, BoolReadWidget),
    (zope.schema.interfaces.IInt, None),
    (zope.schema.interfaces.IFloat, None),
    (zope.schema.interfaces.IDatetime, None),
    (zope.schema.interfaces.IChoice, ChoiceReadWidget),
    (zope.schema.interfaces.IDottedName, None),
    (zope.schema.interfaces.IURI, None),
    (zope.schema.interfaces.IList, ListReadWidget),
    (zope.schema.interfaces.ITuple, ListReadWidget),
    (zope.schema.interfaces.IDict, DictReadWidget),
    (zope.schema.interfaces.IObject, None),
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
    (zope.schema.interfaces.IList, ListEditWidget),
    (zope.schema.interfaces.ITuple, ListEditWidget),
    (zope.schema.interfaces.IDict, DictEditWidget),
    (zope.schema.interfaces.IObject, None),
]

for field_iface, widget_cls in default_widgets:
    if widget_cls:
        register_field_widget(field_iface, widget_cls)

