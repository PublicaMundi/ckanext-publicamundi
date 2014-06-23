import zope.interface
import zope.schema

class IWidget(zope.interface.Interface):

    action = zope.schema.Choice(('read', 'edit'))

    qualifiers = zope.schema.List(value_type=zope.schema.DottedName())
    
    is_fallback = zope.schema.Bool()

    def get_template():
        '''Return a filename for a template'''

    def prepare_template_vars(data):
        '''Prepare and return context data before rendering the widget.
        '''

    def render(data):
        '''Generate markup'''

class IFieldWidget(IWidget):

    def prepare_template_vars(name_prefix, data):
        '''Prepare context before rendering the widget'''

    def render(name_prefix, data):
        '''Generate markup'''

class IObjectWidget(IWidget):

    def get_omitted_fields():
        '''Return a list of fields that should be omitted from rendering'''

    def prepare_template_vars(name_prefix, data):
        '''Prepare context before rendering the widget'''

    def render(name_prefix, data):
        '''Generate markup'''

