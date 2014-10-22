import zope.interface
import zope.schema
import zope.schema.vocabulary
import copy
from collections import OrderedDict

import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.util import raise_for_stub_method
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata.base import Object, FieldContext
from ckanext.publicamundi.lib.metadata.widgets.ibase import (
    IWidget, IFieldWidget, IObjectWidget)
from ckanext.publicamundi.lib.metadata.widgets import (
    QualAction, LookupContext, markup_for_object, markup_for_field)
from ckanext.publicamundi.lib.metadata.widgets.util import to_c14n_markup

#
# Base
#

class Widget(object):
    
    zope.interface.implements(IWidget)
    
    action = None

    context = None

    errors = None
     
    _reserved_var_names = [
        'name_prefix', 'action', 'requested_action', 'provided_action',
    ]
   
    def get_template(self):
        raise_for_stub_method()

    def prepare_template_vars(self, data):
        return copy.deepcopy(data)

    def render(self, data):
        raise_for_stub_method()
    
    @property
    def qualified_action(self):
        '''Return a qualified action (as a string) provided by this widget'''
        if self.context:
            return self.context.provided_action.to_string()
        else:
            return QualAction(self.action).to_string()

class FieldWidget(Widget):
    
    zope.interface.implements(IFieldWidget)
    
    _reserved_var_names = [
        'name_prefix', 
        'action', 'requested_action', 'provided_action',
        'name', 'field', 'value',
    ]

    def __init__(self, field, *args):
        # Check adaptee: 1st argument must be a bound field
        assert isinstance(field, zope.schema.Field)
        assert field.context and isinstance(field.context, FieldContext)
        # Initialize
        self.field = field
        self.name = field.context.key
        self.value = field.context.value
        self.context = None
        self.errors = None
    
    ## IFieldWidget interface ##
    
    def prepare_template_vars(self, name_prefix, data):
        '''Prepare template context'''

        # Provide basic variables
        tpl_vars = {
            'name_prefix': name_prefix,
            'action': self.action,
            'requested_action': self.context.requested_action,
            'provided_action': self.context.provided_action,
            'field': self.field,
            'value': self.value,
            'name': self.name,
            'errors': self.errors,
            'required': self.field.required,
            'title': self.field.title,
            'description': self.field.description,
            'readonly': self.field.readonly,
            'attrs': {},
            'classes': [],
        }

        # Override with caller's variables
        
        for k in data:
            if not k in self._reserved_var_names:
                tpl_vars[k] = data[k]

        # Provide computed variables or sensible defaults
        
        qname = "%s%s" %(name_prefix + '.' if name_prefix else '', 
            tpl_vars['name'])
        tpl_vars['qname'] = qname
        tpl_vars['classes'] = tpl_vars['classes'] + [
            'widget',
            'field-widget', 
            'field-%s-widget' %(self.action),
            'field-qname-%s' %(qname),]

        return tpl_vars

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        tpl_vars = self.prepare_template_vars(name_prefix, data)
        markup = toolkit.render_snippet(tpl, tpl_vars)
        return markup

class ObjectWidget(Widget):
    
    zope.interface.implements(IObjectWidget)
    
    _reserved_var_names = [
        'name_prefix', 
        'action', 'requested_action', 'provided_action',
        'obj', 'schema',
    ]

    def __init__(self, obj):
        assert isinstance(obj, Object)
        self.obj = obj
        self.context = None
        self.errors = None

    def get_glue_template(self):
        '''Provide a template responsible to glue (rendered) fields together'''
        return 'package/snippets/objects/glue-%(action)s.html' %(
            dict(action=self.action))

    def get_field_qualifiers(self):
        '''Return an ordered map of (field, qualifier) items to be used in glue
        template.

        If no valid template is provided (via get_template()), then we attempt to 
        render a  widget by glue-ing its fields together. In this case, each field is 
        rendered using a "proper" qualifier for it. 
        
        If a certain field is not contained (as a key) in this map, it will not be 
        rendered (when using the glue template). If the relevant key exists, but the
        value is considered zero (e.g. None or '') then we fallback to other ways of
        determining the "proper" qualifier for the field.

        We search for a "proper" qualifier by examining the following (in this order):

         * a non-zero qualifier returned by get_field_qualifiers()
         * a non-zero qualifier tagged directly to the field as 'widget-qualifier'
         * the qualifier used at self.provided_action
        
        Example:

        >>> widget1.get_field_qualifiers()
        OrderedDict([('title', None), ('url', None), ('contacts', 'contacts.foo')])

        '''
        
        # This base implementation returns all fields mapped to a zero qualifier.
        # Note that this result maintains the order that fields had when defined 
        # at the original schema definition.
        
        keys = self.obj.get_field_names(order=True)
        return OrderedDict(((k, None) for k in keys))
    
    def get_field_template_vars(self):
        '''Return a map of (field, data) to be used as template variables in glue 
        template.

        Note: 
        For reasons of caching, a derived schema-specific widget may choose to 
        re-define this method as a classmethod (perhaps combined with a memoizer?).
        '''
        return {}

    ## IObjectWidget interface ##

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare template context'''

        # Provide basic variables
        tpl_vars = {
            'name_prefix': name_prefix,
            'action': self.action,
            'requested_action': self.context.requested_action,
            'provided_action': self.context.provided_action,
            'obj': self.obj,
            'errors': self.errors,
            'schema': self.obj.get_schema(),
            'classes': [],
            'attrs': {},
        }

        # Override with caller's variables
        
        for k in data:
            if not k in self._reserved_var_names:
                tpl_vars[k] = data[k]

        # Provide computed variables and sensible defaults
        qname = name_prefix
        tpl_vars['qname'] = qname
        tpl_vars['classes'] = tpl_vars['classes'] + [
            'widget',
            'object-widget',
            'object-%s-widget' %(self.action),
            'object-qname-%s' %(qname or 'NONE'),]

        return tpl_vars

    def get_template(self):
        return None

    def render(self, name_prefix, data={}):
        
        tpl_vars = self.prepare_template_vars(name_prefix, data)
        tpl = self.get_template()
        obj = self.obj

        if not tpl:
            # No template supplied: use a template to glue fields together.
            # Prepare all additional vars needed for this kind of template.
            tpl = self.get_glue_template()
            
            errors = self.errors
            error_dict = errors if isinstance(errors, dict) else None

            field_qualifiers = self.get_field_qualifiers().iteritems()
            field_data = self.get_field_template_vars()

            def render_field(k, qf):
                f = obj.get_field(k)
                if not qf:
                    qf = f.queryTaggedValue('widget-qualifier')
                if not qf:
                    qf = self.context.provided_action.qualifier
                qa = QualAction(self.action, qualifier=qf)
                ef = error_dict.get(k) if error_dict else None
                df = field_data.get(k, {})
                mf = markup_for_field(qa, f, 
                    errors=ef, name_prefix=name_prefix, data=df)
                return dict(field=f, markup=mf)
            
            tpl_vars['fields'] = OrderedDict(
                ((k, render_field(k, qf)) for k, qf in field_qualifiers))
        
        markup = toolkit.render_snippet(tpl, tpl_vars)
        return markup

#
# Base readers and editors
#

class ReadFieldWidget(FieldWidget):

    action = 'read'

class EditFieldWidget(FieldWidget):

    action = 'edit'
    
class ReadObjectWidget(ObjectWidget):

    action = 'read'

class EditObjectWidget(ObjectWidget):

    action = 'edit'

    def get_readonly_fields(self):
        fields = []
        for k, F in self.obj.get_fields().items():
            if F.readonly:
                fields.append(k)
        return fields

#
# Base widget mixins for container fields 
#

class ContainerFieldWidgetTraits(FieldWidget):
    
    def get_item_qualifier(self):
        qa = self.context.provided_action.make_child('item')
        return qa.qualifier
        
class ListFieldWidgetTraits(ContainerFieldWidgetTraits):

    def get_item_template_vars(self, index=None):
        return {
            'title': '%s #%s' % (
                self.field.value_type.title, 
                str(index + 1) if isinstance(index, int) else '{{index1}}'),
        }
        
    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template.
        The markup for items will be generated before the template is
        called, as it will only act as glue.
        '''
        
        field, value = self.field, self.value
        errors = self.errors
        error_dict = errors if isinstance(errors, dict) else None

        tpl_vars = FieldWidget.prepare_template_vars(self, name_prefix, data)
        title = tpl_vars.get('title')
        qname = tpl_vars.get('qname')
        qa = QualAction(self.action, self.get_item_qualifier())
        
        items = enumerate(value) if value else ()

        def render_item_template():
            yf = field.value_type.bind(FieldContext(key='{{key}}', value=None))
            yd = self.get_item_template_vars(index=None)
            return {
                'variables': ['key', 'title', 'index', 'index1'],
                'markup': to_c14n_markup(
                    markup_for_field(qa, yf, name_prefix=qname, data=yd),
                    with_comments=False)
            }
        
        def render_item(i, y):
            yf = field.value_type.bind(FieldContext(key=i, value=y))
            ye = error_dict.get(i) if error_dict else None
            yd = self.get_item_template_vars(index=i)
            return {
                'index': i,
                'markup': markup_for_field(
                    qa, yf, errors=ye, name_prefix=qname, data=yd)
            }
        
        tpl_vars.update({
            'item_template': render_item_template(),
            'items': [render_item(i,y) for i, y in items],
        })
        
        return tpl_vars

class DictFieldWidgetTraits(ContainerFieldWidgetTraits):

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template.
        The markup for items will be generated before the template is
        called, as it will only act as glue.
        '''
        
        field, value = self.field, self.value
        assert isinstance(field.key_type, zope.schema.Choice)
        
        errors = self.errors
        error_dict = errors if isinstance(errors, dict) else None

        tpl_vars = FieldWidget.prepare_template_vars(self, name_prefix, data)
        title = tpl_vars.get('title')
        qname = tpl_vars.get('qname')
        qa = QualAction(self.action, self.get_item_qualifier())
        
        terms = field.key_type.vocabulary.by_value
        items = value.items() if value else ()
        
        def render_item_template():
            yf = field.value_type.bind(FieldContext(key='{{key}}', value=None))
            yd = { 'title': '{{title}}' }
            return {
                'variables': ['key', 'title'],
                'markup': to_c14n_markup(
                    markup_for_field(qa, yf, name_prefix=qname, data=yd),
                    with_comments=False)
            }

        def render_item(k, y):
            yf = field.value_type.bind(FieldContext(key=k, value=y))
            term = terms.get(k)
            ye = error_dict.get(k) if error_dict else None
            yd = { 'title': term.title or term.token }
            return {
                'key': k,
                'key_term': term,
                'markup': markup_for_field(
                    qa, yf, errors=ye, name_prefix=qname, data=yd),
            }

        tpl_vars.update({
            'terms': { k: { 'title': v.title, 'token': v.token } 
                for k, v in terms.iteritems() },
            'item_template': render_item_template(),
            'items': { k: render_item(k,y) for k,y in items if k in terms },
        })
        
        return tpl_vars

#
# Base widgets for object-related fields
#

class ObjectFieldWidgetTraits(FieldWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template.
        
        The markup for the object will be generated here, i.e before the 
        actual template is called to render().
        '''
        
        tpl_vars = FieldWidget.prepare_template_vars(self, name_prefix, data)
        field, value = self.field, self.value
        qname = tpl_vars.get('qname')
        
        # If value is None, pass an empty (but structured) object created
        # from the default factory
        if value is None:
            factory = Object.Factory(self.field.schema)
            value = factory()
        
        # Build the template context for the object's widget: some variables
        # must be moved to the object's context,
        data1 = {}
        for k in ['title', 'description', 'required', 'readonly']:
            v = tpl_vars.pop(k, None)
            if v: 
                data1[k] = v
        
        # Generate markup for the object, feed to the current template context
        qa = self.context.requested_action
        markup = markup_for_object(qa, value, 
            errors=self.errors, name_prefix=qname, data=data1)
        tpl_vars['content'] = { 'markup': markup }
        
        return tpl_vars

