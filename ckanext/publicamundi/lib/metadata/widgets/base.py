import zope.interface
import zope.schema
import zope.schema.vocabulary
import copy

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
        tpl_vars['classes'] = tpl_vars['classes'] + [\
            'widget',
            'field-widget', 
            'field-%s-widget' %(self.action),
            'field-qname-%s' %(qname), ]

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
        '''Return a map of (field, qualifier) items.

        If no valid template is provided (via get_template()) then we attempt to 
        render a  widget by glue-ing its fields together. In this case, each field is 
        rendered using a "proper" qualifier for it. 

        We search for a "proper" qualifier by examining the following (in this order):

         * a qualifier returned by get_field_qualifiers()
         * a qualifier tagged directly to the field as 'widget-qualifier'
         * a qualifier specified by self.qualified_action

        '''
        return {}
    
    def get_omitted_fields(self):
        '''Return a list of fields that should be omitted from rendering'''
        return None

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
        tpl_vars['classes'] = tpl_vars['classes'] + [\
            'widget',
            'object-widget',
            'object-%s-widget' %(self.action),
            'object-qname-%s' %(qname or 'NONE'), ]

        return tpl_vars

    def get_template(self):
        return None

    def render(self, name_prefix, data={}):
        
        tpl_vars = self.prepare_template_vars(name_prefix, data)
        tpl = self.get_template()
        obj = self.obj

        if not tpl:
            # No template supplied: use a template to glue fields together.
            # We must prepare additional vars for this kind of template
            tpl = self.get_glue_template()
            
            errors = self.errors
            error_dict = errors if isinstance(errors, dict) else None

            field_qualifiers = self.get_field_qualifiers()
            q = self.qualified_action

            def render_field(k):
                f = obj.get_field(k)
                qf = (field_qualifiers.get(k)
                    or f.queryTaggedValue('widget-qualifier')
                    or self.context.provided_action.qualifier)
                q = QualAction(self.action, qualifier=qf).to_string()
                ef = error_dict.get(k) if error_dict else None
                mf = markup_for_field(q, f, errors=ef, name_prefix=name_prefix)
                return dict(field=f, markup=mf)
            
            keys = set(obj.get_field_names()) - set(self.get_omitted_fields())
            tpl_vars['fields'] = { k: render_field(k) for k in keys }
        
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

    def get_omitted_fields(self):
        return []

class EditObjectWidget(ObjectWidget):

    action = 'edit'
    
    def get_omitted_fields(self):
        return []

    def get_readonly_fields(self):
        fields = []
        for k, F in self.obj.get_fields().items():
            if F.readonly:
                fields.append(k)
        return fields

#
# Base widgets for container fields 
#

class ListFieldWidgetTraits(FieldWidget):

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
        a = self.context.provided_action.make_child('item')
        q = a.to_string()
        
        items = enumerate(value) if value else ()

        def render_item_template():
            yf = field.value_type.bind(FieldContext(key='{{index}}', value=None))
            yd = { 'title': '%s #{{index1}}' % (yf.title) }
            return {
                'index': 'index', # placeholder
                'markup': to_c14n_markup(
                    markup_for_field(q, yf, name_prefix=qname, data=yd),
                    with_comments=False)
            }
        
        def render_item(i, y):
            yf = field.value_type.bind(FieldContext(key=i, value=y))
            ye = error_dict.get(i) if error_dict else None
            yd = { 'title': '%s #%d' % (yf.title, i + 1) }
            return {
                'index': i,
                'markup': markup_for_field(
                    q, yf, errors=ye, name_prefix=qname, data=yd)
            }
        
        tpl_vars.update({
            'item_template': render_item_template(),
            'items': [render_item(i,y) for i, y in items],
        })
        
        return tpl_vars

class DictFieldWidgetTraits(FieldWidget):

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
        a = self.context.provided_action.make_child('item')
        q = a.to_string()
        
        terms = field.key_type.vocabulary.by_value
        items = value.items() if value else ()
        
        def render_item_template():
            yf = field.value_type.bind(FieldContext(key='{{key}}', value=None))
            yd = { 'title': '{{title}}' }
            return {
                'key': 'key', # a placeholder
                'markup': to_c14n_markup(
                    markup_for_field(q, yf, name_prefix=qname, data=yd),
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
                    q, yf, errors=ye, name_prefix=qname, data=yd),
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
        q = self.context.requested_action.to_string()
        markup = markup_for_object(q, value, 
            errors=self.errors, name_prefix=qname, data=data1)
        tpl_vars['content'] = { 'markup': markup }
        
        return tpl_vars

