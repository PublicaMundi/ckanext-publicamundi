import zope.interface
import zope.schema
import copy

import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata.base import Object, FieldContext
from ckanext.publicamundi.lib.metadata.widgets.ibase import IWidget 
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import parse_qualified_action
from ckanext.publicamundi.lib.metadata.widgets import markup_for_field
from ckanext.publicamundi.lib.metadata.widgets import markup_for_object
    
## Base

class Widget(object):
    zope.interface.implements(IWidget)
    
    action = None
    
    def get_template(self):
        raise NotImplementedError('Method should be implemented in a derived class')

    def prepare_template_vars(self, data):
        return copy.deepcopy(data)

    def render(self, data):
        raise NotImplementedError('Method should be implemented in a derived class')
    
class FieldWidget(Widget):
    zope.interface.implements(IFieldWidget)

    def __init__(self, field, qualified_action):
        assert isinstance(field, zope.schema.Field)
        assert field.context and isinstance(field.context, FieldContext)
        self.field = field
        action, qualifier = parse_qualified_action(qualified_action)
        assert action == self.action
        self.qualifier = qualifier
        name = field.getName()
        if name:
            # This is a named field, used as an attribute in a
            # schema-providing object
            assert name == field.context.key
            self.name = name
            self.value = field.get(field.context.obj)
        else:
            # This is an anonymous field, probably created from
            # a nested field declaration (e.g. as a List.value_type)
            self.name = field.context.key
            self.value = field.context.obj[field.context.key]
        return
    
    @property
    def qualified_action(self):
        return self.action + \
            (':' + self.qualifier if self.qualifier else '')

    ## IFieldWidget interface ##
    
    def prepare_template_vars(self, name_prefix, data):
        '''Prepare template context'''

        # Provide basic variables
        template_vars = {
            'name_prefix': name_prefix,
            'action': self.action,
            'qualified_action': self.qualified_action,
            'field': self.field,
            'value': self.value,
            'name': self.name,
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
        qname = "%s.%s" %(name_prefix, template_vars['name'])
        template_vars['qname'] = qname
        template_vars['classes'] = template_vars['classes'] + \
            [ 'field-%s-%s' %(self.action, qname), ]

        return template_vars

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        data = self.prepare_template_vars(name_prefix, data)
        markup = toolkit.render_snippet(tpl, data)
        return toolkit.literal(markup)

class ObjectWidget(Widget):
    zope.interface.implements(IObjectWidget)

    def __init__(self, obj, qualified_action):
        assert isinstance(obj, Object)
        self.obj = obj
        action, qualifier = parse_qualified_action(qualified_action)
        assert action == self.action
        self.qualifier = qualifier
    
    @property
    def qualified_action(self):
        return self.action + \
            (':' + self.qualifier if self.qualifier else '')

    ## IObjectWidget interface ##

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare template context'''

        # Provide basic variables
        template_vars = {
            'name_prefix': name_prefix,
            'action': self.action,
            'qualified_action': self.qualified_action,
            'obj': self.obj,
            'schema': self.obj.get_schema(),
            'classes': [],
            'attrs': {},
        }

        # Override with caller's variables
        template_vars.update(data)

        # Provide computed variables and sensible defaults
        qname = name_prefix
        template_vars['qname'] = qname
        template_vars['classes'] = template_vars['classes'] + \
            [ 'object-%s-%s' %(self.action, qname), ]

        return template_vars

    def get_template(self):
        return None

    def get_omitted_fields(self):
        return None

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        if tpl:
            data = self.prepare_template_vars(name_prefix, data)
            markup = toolkit.render_snippet(tpl, data)
        else:
            # Todo
            markup = '<h3>hellooooo object</h3>'
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
        return self._get_readonly_fields()

    def _get_readonly_fields(self):
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
        item_action = '%s:item%s' %(self.action, \
            ('.' + self.qualifier if self.qualifier else ''))
        def render_item(item):
            i, y = item
            assert isinstance(i, int)
            yf = field.value_type.bind(FieldContext(key=i, obj=value))
            return {
                'index': i,
                'markup': markup_for_field(item_action, yf, qname, {
                    'title': '%s #%d' %(yf.title, i) 
                }),
            }
        data.update({
            'items': map(render_item, enumerate(value)),
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
        item_action = '%s:item%s' %(self.action, \
            ('.' + self.qualifier if self.qualifier else ''))
        def render_item(item):
            k, y = item
            assert isinstance(k, basestring)
            yf = field.value_type.bind(FieldContext(key=k, obj=value))
            term = field.key_type.vocabulary.getTerm(k)
            return {
                'key': term,
                'markup': markup_for_field(item_action, yf, qname, {
                    'title': term.title or term.token
                }),
            }
        data.update({
            'items': map(render_item, value.iteritems()),
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
        # Build the template context for the object's widget: some variables
        # are moved to the object's context,
        data1 = {}
        for k in ['title', 'description', 'required', 'readonly']:
            v = data.pop(k, None)
            if v: 
                data1[k] = v
        # Generate markup for the contained object, feed result to
        # the current template context
        data.update({
            'obj': {
                'markup': markup_for_object(self.qualified_action, value, qname, data1)
            }
        })
        return data

