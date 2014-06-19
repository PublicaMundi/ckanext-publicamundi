import zope.interface
import zope.interface.verify
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import Object

from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets import types as object_widgets

def generate_markup_for_field(action, F, f, name_prefix='', **kwargs):
    assert isinstance(F, zope.schema.Field)
    actions = [action]
    try:
        basic_action, variation = action.split('.')
        actions.append(basic_action) # as a fallback
    except ValueError:
        pass
    # Lookup registry
    widget = None
    while not widget and actions:
        name = actions.pop(0)
        widget = adapter_registry.queryMultiAdapter([F, f], IFieldWidget, name)
    if not widget:
        raise ValueError('Cannot find an widget adapter for field %s for action %s' %(
            F, action))
    # Found a widget to adapt [F, f]
    assert zope.interface.verify.verifyObject(IFieldWidget, widget)
    return widget.render(name_prefix, kwargs)

def generate_markup_for_object(action, obj, name_prefix='', **kwargs):
    assert isinstance(obj, Object)
    actions = [action]
    try:
        basic_action, variation = action.split('.')
        actions.append(basic_action) # as a fallback
    except ValueError:
        pass
    # Lookup registry
    widget = None
    while not widget and actions:
        name = actions.pop(0)
        widget = adapter_registry.queryMultiAdapter([obj], IObjectWidget, name)
    if not widget:
        raise ValueError('Cannot find an widget adapter for schema %s for action %s' %(
            obj.get_schema(), action))
    # Found a widget to adapt [obj]
    assert zope.interface.verify.verifyObject(IObjectWidget, widget)
    return widget.render(name_prefix, kwargs)

