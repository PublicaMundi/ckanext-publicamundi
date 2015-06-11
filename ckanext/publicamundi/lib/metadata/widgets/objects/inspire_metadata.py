import zope.interface
from collections import OrderedDict

from ckan.plugins import toolkit

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import (
    object_widget_adapter,
    field_widget_adapter,
    field_widget_multiadapter)
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets.base import (
    EditFieldWidget,
    EditObjectWidget, 
    ReadFieldWidget,
    ReadObjectWidget,
    ListFieldWidgetTraits,
    DictFieldWidgetTraits)

from ._common import TableObjectReadWidget

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

@field_widget_multiadapter([IListField, schemata.IGeographicBoundingBox],
    qualifiers=['bounding_box.inspire'], is_fallback=False)
class BoundingBoxEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_item_qualifier(self):
        return 'item'
    
    def get_template(self):
        return 'package/snippets/fields/edit-list-bounding_box-inspire.html'

@field_widget_multiadapter([IListField, schemata.ISpatialResolution],
    qualifiers=['spatial_resolution.inspire'], is_fallback=False)
class SpatialResolutionEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_item_qualifier(self):
        return 'item'
    
    def get_template(self):
        return 'package/snippets/fields/edit-list-spatial_resolution-inspire.html'

@field_widget_multiadapter([IListField, schemata.IConformity],
    qualifiers=['conformity.inspire'], is_fallback=False)
class ConformityEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_item_qualifier(self):
        return 'item'
    
    def get_template(self):
        return 'package/snippets/fields/edit-list-conformity-inspire.html'

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

@field_widget_adapter(ITextField, 
    qualifiers=['lineage.inspire'], is_fallback=False)
class LineageEditWidget(EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-text-lineage-inspire.html'

@field_widget_multiadapter([IListField, ITextLineField],
    qualifiers=['access_constraints.inspire'], is_fallback=False)
class AccessConstraintsEditWidget(EditFieldWidget):
 
    def get_template(self):
        return 'package/snippets/fields/edit-list-textline.html'

@object_widget_adapter(schemata.IInspireMetadata, 
    qualifiers=['datasetform'], is_fallback=True)
class InspireEditWidget(EditObjectWidget):
    
    def get_field_template_vars(self):
        
        # Note We are going to override some field titles because their full names 
        # seem quite verbose when placed in our form (as inputs are already grouped
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
                'verbose': True,
                #'input_classes': ['span5'],
                #'size': 12,
            },
            'keywords': {
                'title': None, #_('Keywords'),
                'verbose': True,
            },
            'temporal_extent': {},
            'creation_date': {},
            'publication_date': {},
            'revision_date': {},
            'lineage': {
                'heading': _('Lineage Statement'),
                'attrs': {
                    'rows': 5,
                }
            },
            'reference_system': {
                'title': _('Coordinate Reference System'),
                'description': _(
                    'The geographical coordinate system (CRS) in which resources are provided.'),
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
            ('bounding_box', 'bounding_box.inspire'),
            ('temporal_extent', 'temporal_extent.inspire'),
            ('creation_date', None),
            ('publication_date', None),
            ('revision_date', None),
            ('lineage', 'lineage.inspire'),
            ('reference_system', None),
            ('spatial_resolution', 'spatial_resolution.inspire'),
            ('responsible_party', 'contacts.inspire'),
            ('conformity', 'conformity.inspire'),
            ('access_constraints', 'access_constraints.inspire'),
            ('limitations', 'access_constraints.inspire'),
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

@object_widget_adapter(schemata.IInspireMetadata, qualifiers=['table'])
class TableInspireReadWidget(TableObjectReadWidget):

    def get_field_order(self):
        return [
           # Identification
           'identifier',
           'title',
           'abstract',
           'locator',
           'resource_language',
           # Metadata on metadata
           'contact',
           'languagecode',
           'datestamp',
           # Classification
           'topic_category',
           # Keywords
           'keywords',
           # Geographic
           'bounding_box',
           # Temporal
           'temporal_extent',
           'creation_date',
           'publication_date',
           'revision_date',
           # Quality - Validity 
           'lineage',
           'reference_system',
           'spatial_resolution',
           # Conformity
           'conformity',
           # Contraints
           'access_constraints',
           'limitations',
           # Responsible Party
           'responsible_party',
        ]

