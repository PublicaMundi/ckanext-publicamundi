import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import Object

from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets import types as object_widgets

def generate_markup_for_field(action, F, f, name_prefix='', **kwargs):
    assert isinstance(F, zope.schema.Field)
    widget = adapter_registry.queryMultiAdapter([F, f], IFieldWidget, action)
    if not widget:
        raise ValueError('Cannot find an widget adapter for field %s for action %s' %(
            F, action))
    return widget.render(name_prefix, kwargs)

def generate_markup_for_object(action, obj, name_prefix='', **kwargs):
    assert isinstance(obj, Object)
    widget = adapter_registry.queryMultiAdapter([obj], IObjectWidget, action)
    if not widget:
        raise ValueError('Cannot find an widget adapter for schema %s for action %s' %(
            obj.get_schema(), action))
    return widget.render(name_prefix, kwargs)

