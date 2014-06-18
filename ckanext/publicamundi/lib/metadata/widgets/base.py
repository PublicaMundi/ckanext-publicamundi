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

    def get_template(self):
        raise NotImplementedError('This method should be defined in a derived class')

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        data.update({
            'name_prefix': name_prefix,
            'value': self.field_val,
            'F': self.field_def,
        })
        markup = toolkit.render_snippet(tpl, data)
        return toolkit.literal(markup)

class ObjectWidget(object):
    zope.interface.implements(IObjectWidget)

    action = ''

    def __init__(self, obj):
        assert isinstance(obj, Object)
        self.obj = obj

    def get_template(self):
        raise NotImplementedError('This method should be defined in a derived class')

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        data.update({
            'name_prefix': name_prefix,
            'obj': self.obj,
        })
        markup = toolkit.render_snippet(tpl, data)
        return toolkit.literal(markup)


class ReadFieldWidget(FieldWidget):
    action = 'read'

class EditFieldWidget(FieldWidget):
    action = 'edit'

class ReadObjectWidget(ObjectWidget):
    action = 'read'

class EditObjectWidget(ObjectWidget):
    action = 'edit'

