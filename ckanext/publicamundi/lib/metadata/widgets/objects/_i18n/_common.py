from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets.objects import _common as common_widgets

@object_widget_adapter(schemata.IObject, qualifiers=['table.translatable'])
class TableReadWidget(common_widgets.TableReadWidget):

    markup_qualifier = 'td.translatable'

    def get_template(self):
        return 'package/snippets/objects/read-object-table-translatable.html'

@field_widget_adapter(ITextField, 
    qualifiers=['dd.translatable', 'td.translatable'])
@field_widget_adapter(ITextLineField, 
    qualifiers=['dd.translatable', 'td.translatable'])
class DataTextReadWidget(base_widgets.ReadFieldWidget):
    
    def get_template(self):
        return 'package/snippets/fields/read-text-dd-translatable.html'
 
    def prepare_template_vars(self, name_prefix, data):
        parent = super(DataTextReadWidget, self)
        tpl_vars = parent.prepare_template_vars(name_prefix, data)
        tpl_vars['translatable'] = self.field.queryTaggedValue('translatable')
        return tpl_vars

@object_widget_adapter(schemata.IObject, 
    qualifiers=['td.translatable', 'dd.translatable'])
class TdObjectReadWidget(base_widgets.ReadObjectWidget):
    
    def get_field_qualifiers(self):
        qualifiers = super(TdObjectReadWidget, self).get_field_qualifiers()
        for key in qualifiers:
            qualifiers[key] = 'dd.translatable'
        return qualifiers

    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-object-td.html'

@object_widget_adapter(schemata.IObject,
    qualifiers=['dl.translatable'])
class DlObjectReadWidget(base_widgets.ReadObjectWidget):
    
    def get_field_qualifiers(self):
        qualifiers = super(DlObjectReadWidget, self).get_field_qualifiers()
        for key in qualifiers:
            qualifiers[key] = 'dd.translatable'
        return qualifiers

    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-object-dl.html'

@field_widget_adapter(ITupleField, 
    qualifiers=['td.translatable', 'dd.translatable', 'dl.translatable'])
@field_widget_adapter(IListField, 
    qualifiers=['td.translatable', 'dd.translatable', 'dl.translatable'])
class ListFieldReadWidget(field_widgets.ListReadWidget):

    def get_item_qualifier(self):
        return 'dd.translatable'

