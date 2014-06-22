import zope.interface
import zope.schema

from ckan.plugins import toolkit

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import Object, FieldContext
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import markup_for_field
from ckanext.publicamundi.lib.metadata.widgets import markup_for_object

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

class ListEditWidget(base_widgets.EditFieldWidget):

    action = 'edit'

    def __init__(self, field):
        assert \
            isinstance(field, zope.schema.List) or \
            isinstance(field, zope.schema.Tuple)
        base_widgets.EditFieldWidget.__init__(self, field)

    def get_template(self):
        return 'package/snippets/fields/edit-list.html'

    def set_template_vars(self, name_prefix, data):
        '''Prepare data for the template.
        The markup for items will be generated before the template is
        called, as it will only act as glue.
        '''
        data = base_widgets.EditFieldWidget.set_template_vars(self, name_prefix, data)
        field = self.field
        value = self.value
        title = data['title']
        qname = data['qname']
        basic_action = data['basic_action']
        item_prefix = qname
        item_action = '%s.list-item' %(basic_action)
        def render_item(item):
            i, y = item
            item_data = {
                'title': u'%s #%d' %(title, i),
            }
            yf = field.value_type.bind(FieldContext(key=i, obj=value))
            return {
                'index': i,
                'markup': markup_for_field(item_action, yf, item_prefix, item_data)
            }
        data.update({
            'items': map(render_item, enumerate(value)),
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'list'),
            ]),
        })
        return data

# Readers #

class TextReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-text.html'

class BoolReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-bool.html'

class ChoiceReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-choice.html'

class ListReadWidget(base_widgets.ReadFieldWidget):

    action = 'read'

    def get_template(self):
        return 'package/snippets/fields/read-list.html'

    def set_template_vars(self, name_prefix, data):
        data = base_widgets.ReadFieldWidget.set_template_vars(self, name_prefix, data)
        # Todo
        return data

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
    (zope.schema.interfaces.IList, ListReadWidget),
    (zope.schema.interfaces.ITuple, ListReadWidget),
    (zope.schema.interfaces.IDict, None),
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
    (zope.schema.interfaces.IDict, None),
    (zope.schema.interfaces.IObject, None),
]

for field_iface, widget_cls in default_widgets:
    if widget_cls:
        register_field_widget(field_iface, widget_cls)

