import zope.interface
from collections import OrderedDict

from ckan.plugins import toolkit

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets.base import (
    EditFieldWidget, EditObjectWidget, 
    ReadFieldWidget, ReadObjectWidget,
    ListFieldWidgetTraits, DictFieldWidgetTraits)

_ = toolkit._

@field_widget_multiadapter([IListField, schemata.IResponsibleParty],
    qualifiers=['contacts.inspire'], is_fallback=False)
class ListOfContactsEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_template(self):
        return 'package/snippets/fields/edit-list-contacts-inspire.html'

@object_widget_adapter(schemata.IInspireMetadata, 
    qualifiers=['datasetform'], is_fallback=True)
class InspireEditWidget(EditObjectWidget):

    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(InspireEditWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
    
    def get_field_template_vars(self):
        
        # Note We are going to override some field titles because their full names 
        # seem quite verbose when placed in our form (as inputs are allready grouped
        # in accordion sections).
        
        return {
            'languagecode': {
                'title': _('Language'),
            },
            'datestamp': {
                'title': _('Date Updated'),
            },
            'contact': {
                'title': _('Contact Points'),
            },
        }

    def get_field_qualifiers(self):
        return OrderedDict([
            ('contact', 'contacts.inspire'),
            ('languagecode', 'select2'),
            ('datestamp', None),
        ])
        
    def get_glue_template(self):
        return 'package/snippets/objects/glue-edit-inspire-datasetform.html'
    
    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IInspireMetadata)
class InspireReadWidget(ReadObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(InspireReadWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
     
    def get_field_qualifiers(self):
        return OrderedDict([
            ('languagecode', None),
            ('datestamp', None),
        ])

    def get_template(self):
        return None # use glue template

