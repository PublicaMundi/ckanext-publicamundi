import zope.interface

from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata import types as types

class PointEditFieldWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/types/edit-point.html'

class PointReadFieldWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/types/read-point.html'

