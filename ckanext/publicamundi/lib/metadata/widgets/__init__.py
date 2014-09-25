import re
import zope.interface
import zope.interface.verify
import zope.schema
import logging

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata import (
    adapter_registry, IObject, Object, FieldContext)

from ckanext.publicamundi.lib.metadata.widgets.ibase import (
    IQualAction, ILookupContext, 
    IWidget, IFieldWidget, IObjectWidget)

# Qualified action

class QualAction(object):
    
    zope.interface.implements(IQualAction)
    
    __slots__ = ('action', 'qualifier')

    def __init__(self, action=None, qualifier=None):
        IQualAction.get('action').validate(action)
        self.action = action
        IQualAction.get('qualifier').validate(qualifier)
        self.qualifier = qualifier

    def to_string(self):
        '''Stringify as <action>:<qualifier>'''
        return self.action + \
            (':' + self.qualifier if self.qualifier else '')
   
    __str__ = to_string

    __repr__ = to_string

    def parents(self):
        p = []
        qualifier_parts = self.qualifier.split('.') if self.qualifier else []
        p.append(QualAction(self.action))
        for i in range(1, len(qualifier_parts)):
            p.append(QualAction(
                self.action, qualifier='.'.join(qualifier_parts[:i])))
        return p

    def make_child(self, child_qualifier):
        assert re.match('[a-z][_a-z0-9]+$', child_qualifier), \
            'Not a valid path component for a dotted name'
        q = self.qualifier + '.' + child_qualifier if self.qualifier else child_qualifier
        return QualAction(self.action, q)

    @classmethod
    def from_string(cls, q):
        ''' Parse <action>:<qualifier> '''
        try:
            action, qualifier = q.split(':')
        except:
            action, qualifier = q, None
        return cls(action, qualifier)

# Context for widget adaptation
 
class LookupContext(object):
    
    zope.interface.implements(ILookupContext)

    __slots__ = ('requested_action', 'provided_action')
    
    def __init__(self, requested=None, provided=None):
        self.requested_action = requested
        self.provided_action = provided

# Exception for adaptation failures

class WidgetNotFound(Exception):
    
    def __init__(self, qualified_action, r):
        self.qualified_action = qualified_action
        self.r = r

    def __str__(self):
        return 'Cannot find a widget for %s for action "%s"' %(
            type(self.r).__name__, self.qualified_action)

# Decorators for widget adapters

def decorator_for_widget_multiadapter(required_ifaces, provided_iface, qualifiers, is_fallback):
    def decorate(widget_cls):
        assert provided_iface.implementedBy(widget_cls) 
        names = set()
        action = widget_cls.action
        if is_fallback or not qualifiers:
            names.add(action)
        for qualifier in qualifiers:
            q = QualAction(action=action, qualifier=qualifier)
            names.add(q.to_string())
        for name in names:
            adapter_registry.register(required_ifaces, provided_iface, name, widget_cls)
        return widget_cls
    return decorate
   
def field_widget_adapter(field_iface, qualifiers=[], is_fallback=False):
    assert field_iface.extends(IField)
    decorator = decorator_for_widget_multiadapter(
        [field_iface], IFieldWidget, qualifiers, is_fallback)
    return decorator

def field_widget_multiadapter(field_ifaces, qualifiers=[], is_fallback=False):
    for iface in field_ifaces:
        assert iface.extends(IField)
    decorator = decorator_for_widget_multiadapter(
        field_ifaces, IFieldWidget, qualifiers, is_fallback)
    return decorator
      
def object_widget_adapter(object_iface, qualifiers=[], is_fallback=False):
    assert object_iface.isOrExtends(IObject)
    decorator = decorator_for_widget_multiadapter(
        [object_iface], IObjectWidget, qualifiers, is_fallback)
    return decorator

# Utilities

def widget_for_object(qualified_action, obj, errors=None):
    '''Find and instantiate a widget to adapt an object to a widget interface.
    '''
    
    # Build an array with all candidate names
    q = QualAction.from_string(qualified_action)
    candidates = list(reversed(q.parents() + [q]))

    # Lookup registry
    widget = None
    for candidate in candidates:
        name = candidate.to_string()
        widget = adapter_registry.queryMultiAdapter([obj], IObjectWidget, name)
        logger.debug('Trying to adapt [%s] to widget for action "%s": %s',
            type(obj).__name__, name, 
            widget.cls_name() if widget else 'NONE')
        if widget:
            break
    
    if widget:
        widget.context = LookupContext(requested=q, provided=candidate)
        widget.errors = errors
    else:
        raise WidgetNotFound(qualified_action, obj)
    
    # Found a widget to adapt to obj
    assert zope.interface.verify.verifyObject(IObjectWidget, widget)
    return widget

def widget_for_field(qualified_action, field, errors=None):
    '''Find and instantiate a widget to adapt a field to a widget interface.
    The given field should be a bound instance of zope.schema.Field.
    '''
    
    # Build an array with all candidate names
    q = QualAction.from_string(qualified_action)
    candidates = list(reversed(q.parents() + [q]))

    # Build adaptee vector
    adaptee = [field]
    y = field
    while IContainerField.providedBy(y):
        adaptee.append(y.value_type)
        y = y.value_type
     
    # Lookup registry
    widget = None
    while len(adaptee):
        for candidate in candidates:
            name = candidate.to_string()
            widget = adapter_registry.queryMultiAdapter(adaptee, IFieldWidget, name)
            logger.debug('Trying to adapt [%s] to widget for action "%s": %s',
                ', '.join([type(x).__name__ for x in adaptee]), name, 
                widget.cls_name() if widget else 'NONE')
            if widget:
                break
        if widget:
            break
        # Fall back to a more general version of this adaptee    
        adaptee.pop()
    
    if widget:
        widget.context = LookupContext(requested=q, provided=candidate)
        widget.errors = errors
    else:
        raise WidgetNotFound(qualified_action, field)
    
    # Found a widget to adapt to field
    assert zope.interface.verify.verifyObject(IFieldWidget, widget)
    return widget

def markup_for_field(qualified_action, field, errors=None, name_prefix='', data={}):
    assert isinstance(field, zope.schema.Field)
    widget = widget_for_field(qualified_action, field, errors)
    return widget.render(name_prefix, data)

def markup_for_object(qualified_action, obj, errors=None, name_prefix='', data={}):
    assert isinstance(obj, Object)
    widget = widget_for_object(qualified_action, obj, errors)
    return widget.render(name_prefix, data)

# Import actual widgets

from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets import objects as object_widgets

