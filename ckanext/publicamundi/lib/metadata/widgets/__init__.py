import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import BaseObject

from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets.base import FieldWidget, ObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import read as read_widgets
from ckanext.publicamundi.lib.metadata.widgets import edit as edit_widgets

def generate_markup_for_field(action, F, f, name_prefix='', title=None, description=None):
    assert isinstance(F, zope.schema.Field)
    widget = adapter_registry.queryMultiAdapter([F, f], IFieldWidget, action)
    if not widget:
        raise ValueError('Cannot find an widget adapter for field %s for action %s' %(
            F, action))
    return widget.render(name_prefix, {
        'title': title,
        'description': description,
        'errors': [], # Todo 
    })

def generate_markup_for_object(action, obj, name_prefix='', title=None, description=None):
    assert isinstance(obj, BaseObject)
    # Todo
    pass

adapter_registry.register([zope.schema.interfaces.IText, None],
    IFieldWidget, 'read', read_widgets.TextFieldWidget)

adapter_registry.register([zope.schema.interfaces.ITextLine, None],
    IFieldWidget, 'read', read_widgets.TextFieldWidget)

adapter_registry.register([zope.schema.interfaces.IText, None],
    IFieldWidget, 'edit', edit_widgets.TextFieldWidget)

adapter_registry.register([zope.schema.interfaces.ITextLine, None],
    IFieldWidget, 'edit', edit_widgets.TextFieldWidget)

