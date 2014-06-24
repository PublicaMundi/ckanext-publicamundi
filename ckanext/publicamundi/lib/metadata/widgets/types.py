import zope.interface

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata.widgets import object_widget_adapter
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

## Define widgets ##

@object_widget_adapter(schemata.IPoint)
class PointEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-point.html'

@object_widget_adapter(schemata.IPoint)
class PointReadWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-point.html'

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-temporal_extent.html'

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentReadWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-temporal_extent.html'

