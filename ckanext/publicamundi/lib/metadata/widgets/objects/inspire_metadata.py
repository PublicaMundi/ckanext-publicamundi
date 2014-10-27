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
class ContactsEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_template(self):
        return 'package/snippets/fields/edit-list-contacts-inspire.html'

@field_widget_multiadapter([IListField, schemata.ITemporalExtent],
    qualifiers=['temporal_extent.inspire'], is_fallback=False)
class TemporalExtentsEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_item_qualifier(self):
        return 'item'
    
    def get_template(self):
        return 'package/snippets/fields/edit-list-temporal_extent-inspire.html'

@field_widget_multiadapter([IListField, IURIField],
    qualifiers=['locator.inspire'], is_fallback=False)
class ResourceLocatorsEditWidget(EditFieldWidget):
 
    def get_template(self):
        return 'package/snippets/fields/edit-list-locator-inspire.html'

@field_widget_multiadapter([IListField, IChoiceField],
    qualifiers=['resource_language.inspire'], is_fallback=False)
class ResourceLanguagesEditWidget(EditFieldWidget):
 
    def get_template(self):
        return 'package/snippets/fields/edit-list-resource_language-inspire.html'

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
            'identifier': {
                # Note: Not generated here (see glue template)
            },
            'title': {
                # Note: Not generated here (see glue template)
            },
            'abstract': {
                # Note: Not generated here (see glue template)
            },
            'topic_category': {
                'title': _('Topic Category'),
                #'input_classes': ['span5'],
                'verbose': True,
                #'size': 12,
            },
            'keywords': {
                'title': None, #_('Keywords'),
                'verbose': True,
            },
            'temporal_extent': {
            },
            'creation_date': {
            },
            'publication_date': {
            },
            'revision_date': {
            },
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
            #('identifier', 'identifier.inspire'),
            #('title', 'title.inspire'),
            #('abstract', 'abstract.inspire'),
            ('topic_category', 'checkbox'),
            ('keywords', None),
            ('temporal_extent', 'temporal_extent.inspire'),
            ('creation_date', None),
            ('publication_date', None),
            ('revision_date', None),
            ('responsible_party', 'contacts.inspire'),
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

