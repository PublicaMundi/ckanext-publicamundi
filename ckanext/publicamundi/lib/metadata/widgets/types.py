import zope.interface

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.widgets.ibase import IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

## Define widgets ##

class PointEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-point.html'

class PointReadWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-point.html'

class TemporalExtentEditWidget(base_widgets.EditObjectWidget):

    def _get_template(self):
        return 'package/snippets/objects/edit-temporal_extent.html'

class TemporalExtentReadWidget(base_widgets.ReadObjectWidget):

    def _get_template(self):
        return 'package/snippets/objects/read-temporal_extent.html'

## Register adapters ##

def register_object_widget(object_iface, widget_cls):
    for name in widget_cls.get_qualified_actions():
        adapter_registry.register(
            [object_iface, None], IObjectWidget, name, widget_cls)

default_widgets = [
    (schemata.IPoint, PointReadWidget),
    (schemata.IPoint, PointEditWidget),
    (schemata.ITemporalExtent, TemporalExtentReadWidget),
    (schemata.ITemporalExtent, TemporalExtentEditWidget),
]

for object_iface, widget_cls in default_widgets:
    register_object_widget(object_iface, widget_cls)

