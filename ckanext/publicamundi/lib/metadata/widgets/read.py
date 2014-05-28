import zope.interface

from ckanext.publicamundi.lib.metadata.widgets.ibase import IFieldWidget, IObjectWidget
from ckanext.publicamundi.lib.metadata.widgets.base import FieldWidget, ObjectWidget

class TextFieldWidget(FieldWidget):
    
    def get_template(self):
        return 'package/snippets/fields/read-text.html'

