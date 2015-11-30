
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from ckanext.publicamundi.lib.metadata.widgets.objects import inspire as inspire_widgets

from . import _common as common_i18n_widgets

@object_widget_adapter(schemata.IInspireMetadata, qualifiers=['table.translatable'])
class TableReadWidget(common_i18n_widgets.TableReadWidget, inspire_widgets.TableReadWidget):

    def get_field_order(self):
        return inspire_widgets.TableReadWidget.get_field_order(self)
    
