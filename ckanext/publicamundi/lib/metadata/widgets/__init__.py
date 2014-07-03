import re
import zope.interface
import zope.interface.verify
import zope.interface.interfaces
import zope.schema
import logging

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import IObject
from ckanext.publicamundi.lib.metadata import Object, FieldContext

from ckanext.publicamundi.lib.metadata.widgets.ibase import IQualAction, ILookupContext
from ckanext.publicamundi.lib.metadata.widgets.ibase import IWidget
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget

# Qualified action

class QualAction(object):
    zope.interface.implements(IQualAction)

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

    def __init__(self, requested=None, provided=None):
        self.requested_action = requested
        self.provided_action = provided

# Decorators for widget adapters

def field_widget_adapter(field_iface, qualifiers=[], is_fallback=False):
    assert field_iface.extends(zope.schema.interfaces.IField)
    def decorate(widget_cls):
        assert IFieldWidget.implementedBy(widget_cls) 
        names = set()
        action = widget_cls.action
        if is_fallback or not qualifiers:
            names.add(action)
        for qualifier in qualifiers:
            q = QualAction(action=action, qualifier=qualifier)
            names.add(q.to_string())
        for name in names:
            adapter_registry.register([field_iface], IFieldWidget, name, widget_cls)
        return widget_cls
    return decorate

def object_widget_adapter(object_iface, qualifiers=[], is_fallback=False):
    assert object_iface.extends(IObject)
    def decorate(widget_cls):
        assert IObjectWidget.implementedBy(widget_cls) 
        names = set()
        action = widget_cls.action
        if is_fallback or not qualifiers:
            names.add(action)
        for qualifier in qualifiers: 
            q = QualAction(action=action, qualifier=qualifier)
            names.add(q.to_string())
        for name in names:
            adapter_registry.register([object_iface], IObjectWidget, name, widget_cls)
        return widget_cls
    return decorate

# Utilities

def _widget_for(qualified_action, x, target_iface):
    '''Find and instantiate a widget to adapt x to a target interface.

    Note that x is either a zope-based field (i.e. zope.schema.interfaces.IField) or a 
    schema-providing object (i.e. ckanext.publicamundi.lib.metadata.schemata.IObject). 
    '''
    
    # Build an array with all candidate names
    q = QualAction.from_string(qualified_action)
    candidates = q.parents()
    candidates.append(q)

    # Lookup registry
    widget = None
    for candidate in reversed(candidates):
        name = candidate.to_string()
        widget = adapter_registry.queryMultiAdapter([x], target_iface, name)
        logger.debug('Looked up widget for <%s> for action "%s": %s',
            type(x).__name__, name, widget)
        if widget:
            break
    if widget:
        widget.context = LookupContext(requested=q, provided=candidate)
    else:
        raise ValueError('Cannot find a widget for %s for action "%s"' %(
            type(x).__name__, action))
    
    # Found a widget to adapt x
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

# Import actual widgets

from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets import types as object_widgets

