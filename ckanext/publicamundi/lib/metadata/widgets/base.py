import zope.interface
import zope.schema

import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata.base import Object, FieldContext
from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget

## Base

class FieldWidget(object):
    zope.interface.implements(IFieldWidget)

    action = ''

    def __init__(self, field):
        assert isinstance(field, zope.schema.Field)
        assert field.context and isinstance(field.context, FieldContext)
        self.field = field
        name = field.getName()
        if name:
            # This is a named field, used as an attribute in a
            # schema-providing object
            assert name == field.context.key
            self.name = name
            self.value = field.get(field.context.obj)
        else:
            # This is an anonymous field, probably created from
            # a nested field declaration (e.g. a List.value_type)
            self.name = field.context.key
            self.value = field.context.obj[field.context.key]
        return

    ## IFieldWidget interface ##

    def set_template_vars(self, name_prefix, data):
        '''Prepare template context'''

        basic_action = self.action.split('.')[0]

        # Provide basic variables
        template_vars = {
            'name_prefix': name_prefix,
            'action': self.action,
            'basic_action': basic_action,
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
        template_vars['classes'] = template_vars['classes'] + [ 'field-%s-%s' %(basic_action, qname) ]

        return template_vars

    def get_template(self):
        raise NotImplementedError('Method should be implemented in a derived class')

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        data = self.set_template_vars(name_prefix, data)
        markup = toolkit.render_snippet(tpl, data)
        return toolkit.literal(markup)

class ObjectWidget(object):
    zope.interface.implements(IObjectWidget)

    def __init__(self, obj):
        assert isinstance(obj, Object)
        self.obj = obj

    ## IObjectWidget interface ##

    action = ''

    def set_template_vars(self, name_prefix, data):
        '''Prepare template context'''

        # Provide basic variables
        template_vars = {
            'name_prefix': name_prefix,
            'action': self.action,
            'obj': self.obj,
            'schema': self.obj.get_schema(),
        }

        # Override with caller's variables
        template_vars.update(data)

        # Provide computed variables and sensible defaults
        qname = name_prefix
        basic_action = self.action.split('.')[0]
        template_vars.update({
            'qname': qname,
            'classes': [ 'field-%s-%s' %(basic_action, qname), ],
            'attrs': {},
        })

        return template_vars

    def get_template(self):
        return None

    def get_omitted_fields(self):
        return None

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        if tpl:
            data = self.set_template_vars(name_prefix, data)
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

