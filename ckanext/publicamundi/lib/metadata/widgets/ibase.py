import zope.interface

class IWidget(zope.interface.Interface):

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

