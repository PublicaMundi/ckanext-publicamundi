import zope.interface
import zope.schema

class IWidget(zope.interface.Interface):

    action = zope.schema.DottedName()

    def get_template():
        '''Return a filename for a template'''

    def render(data):
        '''Generate markup'''

class IFieldWidget(IWidget):

    def render(name_prefix, data):
        '''Generate markup'''

class IObjectWidget(IWidget):

    def render(name_prefix, data):
        '''Generate markup'''

