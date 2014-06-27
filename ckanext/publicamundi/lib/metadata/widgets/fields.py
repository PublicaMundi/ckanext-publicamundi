import zope.interface
import zope.schema

from ckan.plugins import toolkit

from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import field_widget_adapter

from ckanext.publicamundi.lib import logger

## Define widgets ##

# Todo: Provide readers/editors for:
#  - IBytes
#  - IInt
#  - IFloat
#  - IDatetime
#  - IDottedName
#  - IURI

# Editors #

@field_widget_adapter(zope.schema.interfaces.IText)
class TextEditWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-text.html'

@field_widget_adapter(zope.schema.interfaces.IBytesLine)
@field_widget_adapter(zope.schema.interfaces.ITextLine)
class TextLineEditWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-textline.html'

@field_widget_adapter(zope.schema.interfaces.IBool)
class BoolEditWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-checkbox-1.html'

@field_widget_adapter(zope.schema.interfaces.IChoice)
class ChoiceEditWidget(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-choice.html'

@field_widget_adapter(zope.schema.interfaces.IList)
@field_widget_adapter(zope.schema.interfaces.ITuple)
class ListEditWidget(base_widgets.EditFieldWidget, base_widgets.ListFieldWidgetTraits):

    def __init__(self, field, qualified_action):
        assert \
            isinstance(field, zope.schema.List) or \
            isinstance(field, zope.schema.Tuple)
        base_widgets.EditFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/edit-list.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.ListFieldWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'list'),
            ]),
        })
        return data

@field_widget_adapter(zope.schema.interfaces.IDict)
class DictEditWidget(base_widgets.EditFieldWidget, base_widgets.DictFieldWidgetTraits):

    def __init__(self, field, qualified_action):
        assert isinstance(field, zope.schema.Dict)
        base_widgets.EditFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/edit-dict.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.DictFieldWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'dict'),
            ]),
        })
        return data

@field_widget_adapter(zope.schema.interfaces.IObject)
class ObjectEditWidget(base_widgets.EditFieldWidget, base_widgets.ObjectFieldWidgetTraits):

    def __init__(self, field, qualified_action):
        assert isinstance(field, zope.schema.Object)
        base_widgets.EditFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/edit-object.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.ObjectFieldWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data.get('attrs', {}).items() + [
                ('data-disabled-module', 'object'),
            ]),
        })
        return data

# Readers #

@field_widget_adapter(zope.schema.interfaces.IText)
@field_widget_adapter(zope.schema.interfaces.ITextLine)
@field_widget_adapter(zope.schema.interfaces.IBytesLine)
class TextReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-text.html'

@field_widget_adapter(zope.schema.interfaces.ITextLine, qualifiers=['item'])
class TextAsItemReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-text-item.html'

@field_widget_adapter(zope.schema.interfaces.IBool)
class BoolReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-bool.html'

@field_widget_adapter(zope.schema.interfaces.IChoice)
class ChoiceReadWidget(base_widgets.ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-choice.html'

@field_widget_adapter(zope.schema.interfaces.IList)
@field_widget_adapter(zope.schema.interfaces.ITuple)
class ListReadWidget(base_widgets.ReadFieldWidget, base_widgets.ListFieldWidgetTraits):

    def __init__(self, field, qualified_action):
        assert \
            isinstance(field, zope.schema.List) or \
            isinstance(field, zope.schema.Tuple)
        base_widgets.ReadFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/read-list.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.ListFieldWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'list'),
            ]),
        })
        return data

@field_widget_adapter(zope.schema.interfaces.IDict)
class DictReadWidget(base_widgets.ReadFieldWidget, base_widgets.DictFieldWidgetTraits):

    def __init__(self, field, qualified_action):
        assert isinstance(field, zope.schema.Dict)
        base_widgets.ReadFieldWidget.__init__(self, field, qualified_action)

    def get_template(self):
        return 'package/snippets/fields/read-dict.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.DictFieldWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data['attrs'].items() + [
                ('data-disabled-module', 'dict'),
            ]),
        })
        return data

@field_widget_adapter(zope.schema.interfaces.IObject)
class ObjectReadWidget(base_widgets.ReadFieldWidget, base_widgets.ObjectFieldWidgetTraits):

    def __init__(self, field, qualified_action):
        assert isinstance(field, zope.schema.Object)
        base_widgets.ReadFieldWidget.__init__(self, field, qualified_action)
    
    def get_template(self):
        return 'package/snippets/fields/read-object.html'

    def prepare_template_vars(self, name_prefix, data):
        '''Prepare data for the template'''
        data = base_widgets.ObjectFieldWidgetTraits.prepare_template_vars(self, name_prefix, data)
        data.update({
            'attrs': dict(data.get('attrs', {}).items() + [
                ('data-disabled-module', 'object'),
            ]),
        })
        return data

