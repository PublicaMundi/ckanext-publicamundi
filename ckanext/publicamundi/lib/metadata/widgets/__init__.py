import zope.interface
import zope.interface.verify
import zope.schema
import logging

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import Object, FieldContext

from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget

logger = logging.getLogger(__name__)

def markup_for_field(action, field, name_prefix='', data={}):
    assert isinstance(field, zope.schema.Field)
    actions = [action]
    try:
        base_action, variation = action.split('.')
        actions.append(base_action) # fallback
    except ValueError:
        pass
    # Lookup registry
    widget = None
    while not widget and actions:
        qualifier = actions.pop(0)
        widget = adapter_registry.queryMultiAdapter([field], IFieldWidget, qualifier)
        logger.debug('Lookup for a widget for field %s for action "%s": %s',
            type(field).__name__, qualifier, widget)
    if not widget:
        raise ValueError('Cannot find a widget for field %s for action %s' %(
            field, action))
    # Found a widget to adapt [field]
    assert zope.interface.verify.verifyObject(IFieldWidget, widget)
    return widget.render(name_prefix, data)

def markup_for_object(action, obj, name_prefix='', data={}):
    assert isinstance(obj, Object)
    schema = obj.schema()
    actions = [action]
    try:
        base_action, variation = action.split('.')
        actions.append(base_action) # fallback
    except ValueError:
        pass
    # Lookup registry
    widget = None
    while not widget and actions:
        qualifier = actions.pop(0)
        widget = adapter_registry.queryMultiAdapter([obj], IObjectWidget, qualifier)
        logger.debug('Lookup for a widget for schema %s for action "%s": %s',
            schema, qualifier, widget)
    if not widget:
        raise ValueError('Cannot find a widget for schema %s for action %s' %(
            schema, action))
    # Found a widget to adapt [obj]
    assert zope.interface.verify.verifyObject(IObjectWidget, widget)
    return widget.render(name_prefix, data)

from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets import types as object_widgets

