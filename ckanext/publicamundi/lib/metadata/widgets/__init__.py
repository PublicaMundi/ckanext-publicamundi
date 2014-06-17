import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import BaseObject

from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets.base import FieldWidget, ObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets

def generate_markup_for_field(action, F, f, name_prefix='', **kwargs):
    assert isinstance(F, zope.schema.Field)
    widget = adapter_registry.queryMultiAdapter([F, f], IFieldWidget, action)
    if not widget:
        raise ValueError('Cannot find an widget adapter for field %s for action %s' %(
            F, action))
    return widget.render(name_prefix, kwargs)

def generate_markup_for_object(action, obj, name_prefix='', **kwargs):
    assert isinstance(obj, BaseObject)
    widget = adapter_registry.queryMultiAdapter([obj], IFieldWidget, action)
    if not widget:
        raise ValueError('Cannot find an widget adapter for schema %s for action %s' %(
            obj.get_schema(), action))
    return widget.render(name_prefix, kwargs)

# Note
# Maybe we should bind action to the widget class (as class attributes?)?
# Consider also using a dotted-name to declare an action variation e.g read.teaser or read.full

default_field_widgets = {
    'read': {
        zope.schema.interfaces.IText: field_widgets.TextReadFieldWidget,
        zope.schema.interfaces.ITextLine: field_widgets.TextReadFieldWidget,
    },
    'edit': {
        zope.schema.interfaces.IText: field_widgets.TextEditFieldWidget,
        zope.schema.interfaces.ITextLine: field_widgets.TextEditFieldWidget,
    }
}

default_object_widgets = {
    'read': {
    },
    'edit': {
    },
}

# Register default widgets

for action, widget_mapping in default_field_widgets.items():
    for field_iface, widget_cls in widget_mapping.items():
        adapter_registry.register([field_iface, None], IFieldWidget, action, widget_cls)

