import zope.interface
import zope.schema

import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import IObject
from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.widgets.ibase import IWidget, IFieldWidget, IObjectWidget

class FieldWidget(object):
    zope.interface.implements(IFieldWidget)

    action = ''

    def __init__(self, F, f):
        assert isinstance(F, zope.schema.Field)
        self.field_val = f
        self.field_def = F

    ## IFieldWidget interface ##

    def get_template(self):
        raise NotImplementedError('Method should be implemented in a derived class')

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        data.update({
            'name_prefix': name_prefix,
            'value': self.field_val,
            'field': self.field_def,
        })
        markup = toolkit.render_snippet(tpl, data)
        return toolkit.literal(markup)

class ObjectWidget(object):
    zope.interface.implements(IObjectWidget)

    def __init__(self, obj):
        assert isinstance(obj, Object)
        self.obj = obj

    ## IObjectWidget interface ##

    action = ''

    def get_template(self):
        return None

    def get_omitted_fields(self):
        return None

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        if tpl:
            data.update({
                'name_prefix': name_prefix,
                'obj': self.obj,
                'schema': self.obj.get_schema(),
            })
            markup = toolkit.render_snippet(tpl, data)
        else:
            # Todo
            markup = '<h3>hellooooo object</h3>'
        return toolkit.literal(markup)


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

