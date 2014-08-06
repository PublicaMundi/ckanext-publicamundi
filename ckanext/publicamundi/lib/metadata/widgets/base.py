import zope.interface
import zope.schema
import copy

import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata.base import Object, FieldContext
from ckanext.publicamundi.lib.util import raise_for_stub_method
from ckanext.publicamundi.lib.metadata.widgets.ibase import IWidget 
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import QualAction, LookupContext
from ckanext.publicamundi.lib.metadata.widgets import markup_for_object
from ckanext.publicamundi.lib.metadata.widgets import markup_for_field
    
## Base

class Widget(object):
    zope.interface.implements(IWidget)
    
    action = None

    context = None

    errors = None
    
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
    
    @classmethod
    def cls_name(cls):
        '''Return a qualified name for this widget class'''
        return '%s.%s' %(cls.__module__, cls.__name__)

class FieldWidget(Widget):
    zope.interface.implements(IFieldWidget)

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
        template_vars = {
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
        template_vars.update(data)

        # Provide computed variables or sensible defaults
        qname = "%s%s" %(name_prefix + '.' if name_prefix else '', 
            template_vars['name'])
        template_vars['qname'] = qname
        template_vars['classes'] = template_vars['classes'] + [\
            'widget',
            'field-widget', 
            'field-%s-widget' %(self.action),
            'field-qname-%s' %(qname), ]

        return template_vars

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        data = self.prepare_template_vars(name_prefix, data)
        markup = toolkit.render_snippet(tpl, data)
        return toolkit.literal(markup)

class ObjectWidget(Widget):
    zope.interface.implements(IObjectWidget)

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
        template_vars = {
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
        template_vars.update(data)

        # Provide computed variables and sensible defaults
        qname = name_prefix
        template_vars['qname'] = qname
        template_vars['classes'] = template_vars['classes'] + [\
            'widget',
            'object-widget',
            'object-%s-widget' %(self.action),
            'object-qname-%s' %(qname), ]

        return template_vars

    def get_template(self):
        return None

    def render(self, name_prefix, data={}):
        data = self.prepare_template_vars(name_prefix, data)
        tpl = self.get_template()
        if not tpl:
            # No template is supplied: use a default template to
            # glue fields together
            tpl = self.get_glue_template()
            # Prepare additional vars needed for the this template:
            # all fields are processed (rendered) and passed to the
            # glue template
            field_qualifiers = self.get_field_qualifiers()
            q = self.qualified_action
            def render_field(k):
                f = self.obj.get_field(k)
                qf = field_qualifiers.get(k) or \
                    f.queryTaggedValue('widget-qualifier') or \
                    self.context.provided_action.qualifier
                q = QualAction(self.action, qualifier=qf).to_string()
                e = self.errors.get(k) if self.errors else None
                return {
                    'field': f,
                    'markup': markup_for_field(q, f, 
                        errors=e, name_prefix=name_prefix, data={}) 
                }
            field_names = set(self.obj.get_field_names()) - \
                set(self.get_omitted_fields())
            data.update({
                'fields': { k: render_field(k) for k in field_names },
            })
        markup = toolkit.render_snippet(tpl, data)
        return toolkit.literal(markup)

## Base readers and editors

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

## Base widgets for fields holding collections 

class ListFieldWidgetTraits(FieldWidget):

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template.
        The markup for items will be generated before the template is
        called, as it will only act as glue.
        '''
        
        field = self.field
        value = self.value
        
        data = FieldWidget.prepare_template_vars(self, name_prefix, data)
        title = data.get('title')
        qname = data.get('qname')
        a = self.context.provided_action.make_child('item')
        q = a.to_string()
        def render_item(i, y):
            assert isinstance(i, int)
            yf = field.value_type.bind(FieldContext(key=i, value=y))
            e = self.errors.get(i) if self.errors else None
            return {
                'index': i,
                'markup': markup_for_field(q, yf, 
                    errors=e, name_prefix=qname, data={ 'title': '%s #%d' %(yf.title, i) }),
            }
        data.update({
            'items': [ render_item(i,y) for i,y in enumerate(value) ],
        })
        
        return data

class DictFieldWidgetTraits(FieldWidget):

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template.
        The markup for items will be generated before the template is
        called, as it will only act as glue.
        '''
        
        field = self.field
        value = self.value
        assert isinstance(field.key_type, zope.schema.Choice)
        
        data = FieldWidget.prepare_template_vars(self, name_prefix, data)
        title = data.get('title')
        qname = data.get('qname')
        a = self.context.provided_action.make_child('item')
        q = a.to_string()
        def render_item(k, y):
            assert isinstance(k, basestring)
            yf = field.value_type.bind(FieldContext(key=k, value=y))
            term = field.key_type.vocabulary.getTerm(k)
            e = self.errors.get(k) if self.errors else None
            return {
                'key': term,
                'markup': markup_for_field(q, yf, 
                    errors=e, name_prefix=qname, data={ 'title': term.title or term.token }),
            }
        data.update({
            'items': { k: render_item(k, y) for k, y in value.iteritems() },
        })

        return data

## Base widgets for fields holding objects

class ObjectFieldWidgetTraits(FieldWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template.
        The markup for the contained object will be generated before the 
        template is called, as it will only act as glue.
        '''
        data = FieldWidget.prepare_template_vars(self, name_prefix, data)
        field = self.field
        value = self.value
        qname = data.get('qname')
        # If value is None, pass an empty (but structured) object created
        # from the default factory
        if value is None:
            factory = Object.Factory(self.field.schema)
            value = factory()
        # Build the template context for the object's widget: some variables
        # are moved to the object's context,
        data1 = {}
        for k in ['title', 'description', 'required', 'readonly']:
            v = data.pop(k, None)
            if v: 
                data1[k] = v
        # Generate markup for the contained object, feed result to
        # the current template context
        q = self.context.requested_action.to_string()
        data.update({
            'obj': {
                'markup': markup_for_object(q, value, 
                    errors=self.errors, name_prefix=qname, data=data1)
            }
        })
        return data

