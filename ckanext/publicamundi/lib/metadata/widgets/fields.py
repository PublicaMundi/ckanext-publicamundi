import zope.interface

from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

class TextEditFieldWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-text.html'

class TextReadFieldWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-text.html'

