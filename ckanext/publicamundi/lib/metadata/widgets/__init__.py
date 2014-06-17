import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import BaseObject

from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets.base import FieldWidget, ObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import read as read_widgets
from ckanext.publicamundi.lib.metadata.widgets import edit as edit_widgets

def generate_markup_for_field(action, F, f, name_prefix='', **kwargs):
    assert isinstance(F, zope.schema.Field)
    widget = adapter_registry.queryMultiAdapter([F, f], IFieldWidget, action)
    if not widget:
        raise ValueError('Cannot find an widget adapter for field %s for action %s' %(
            F, action))
    return widget.render(name_prefix, kwargs)

def generate_markup_for_object(action, obj, name_prefix='', title=None, description=None):
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
     (zope.schema.interfaces.IText, read_widgets.ACTION): read_widgets.TextFieldWidget,
     (zope.schema.interfaces.ITextLine, read_widgets.ACTION): read_widgets.TextFieldWidget,
     (zope.schema.interfaces.IText, edit_widgets.ACTION): edit_widgets.TextFieldWidget,
     (zope.schema.interfaces.ITextLine, edit_widgets.ACTION): edit_widgets.TextFieldWidget,
}

default_object_widgets = {
    
}

# Register default widgets

for (field_iface, action), widget_cls in default_field_widgets.items():
    adapter_registry.register([field_iface, None], IFieldWidget, action, widget_cls)


