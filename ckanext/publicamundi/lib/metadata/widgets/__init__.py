import zope.interface
import zope.interface.verify
import zope.schema
import logging

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import Object, FieldContext

from ckanext.publicamundi.lib.metadata.widgets.ibase import IWidget
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget

logger = logging.getLogger(__name__)

def parse_qualified_action(q):
    ''' Parse <action>:<qualifier> '''
    try:
        action, qualifier = q.split(':')
    except:
        action, qualifier = q, None
    # Validate parts
    try:
        IWidget.get('action').validate(action)
        if qualifier:
            IWidget.get('qualifiers').value_type.validate(qualifier)
    except Exception as ex:
        return None
    return (action, qualifier)

def _widget_for(qualified_action, obj, target_iface):
    '''Find and instantiate a widget to adapt obj to a target interface.
    '''
    # Build an array with all candidate names
    names = []
    action, qualifier = parse_qualified_action(qualified_action)
    names.append(action)
    qualifier_parts = qualifier.split('.') if qualifier else []
    for i in range(0, len(qualifier_parts)):
        names.append('%s:%s' %(action, '.'.join(qualifier_parts[:i+1])))
    # Lookup registry
    widget = None
    while not widget and names:
        name = names.pop()
        widget = adapter_registry.queryMultiAdapter([obj, name], target_iface, name)
        logger.debug('Lookup for a widget for %s for action "%s": %s',
            type(obj).__name__, name, widget)
    if not widget:
        raise ValueError('Cannot find a widget for %s for action %s' %(
            obj, action))
    # Found a widget to adapt obj
    assert zope.interface.verify.verifyObject(target_iface, widget)
    return widget

def markup_for_field(qualified_action, field, name_prefix='', data={}):
    assert isinstance(field, zope.schema.Field)
    widget = _widget_for(qualified_action, field, IFieldWidget)
    return widget.render(name_prefix, data)

def markup_for_object(qualified_action, obj, name_prefix='', data={}):
    assert isinstance(obj, Object)
    widget = _widget_for(qualified_action, obj, IObjectWidget)
    return widget.render(name_prefix, data)

from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets import types as object_widgets

