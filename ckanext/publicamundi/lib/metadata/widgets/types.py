import zope.interface

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.widgets.ibase import IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

## Define widgets ##

class PointEditFieldWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-point.html'

class PointReadFieldWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-point.html'

## Register adapters ##

default_widgets = {
    'read': {
        schemata.IPoint: PointReadFieldWidget,
    },
    'edit': {
        schemata.IPoint: PointEditFieldWidget,
    },
}

for action, widget_mapping in default_widgets.items():
    for object_iface, widget_cls in widget_mapping.items():
        adapter_registry.register([object_iface], IObjectWidget, action, widget_cls)

