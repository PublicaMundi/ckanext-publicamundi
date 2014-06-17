import zope.interface
import zope.schema

import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import IBaseObject
from ckanext.publicamundi.lib.metadata.base import BaseObject
from ckanext.publicamundi.lib.metadata.widgets.ibase import IWidget, IFieldWidget, IObjectWidget

class FieldWidget(object):
    zope.interface.implements(IFieldWidget)

    def __init__(self, F, f):
        assert isinstance(F, zope.schema.Field)
        self.field_value = f
        self.field_def = F

    def get_template(self):
        raise NotImplementedError('This method should be defined in a derived class')

    def render(self, name_prefix, data={}):
        tpl = self.get_template()
        data.update({
            'name_prefix': name_prefix,
            'f': self.field_value,
            'F': self.field_def,
        })
        markup = toolkit.render_snippet(tpl, data)
        return toolkit.literal(markup)

class ObjectWidget(object):
    zope.interface.implements(IObjectWidget)

    def __init__(self, obj):
        assert isinstance(obj, BaseObject)
        self.obj = obj

    def get_template(self):
        raise NotImplementedError('This method should be defined in a derived class')

    def render(self, name_prefix, data={}):
        raise NotImplementedError('Todo')

