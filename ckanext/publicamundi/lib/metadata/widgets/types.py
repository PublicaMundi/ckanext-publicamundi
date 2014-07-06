import zope.interface

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata.widgets import object_widget_adapter
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

## Define widgets ##

# IPoint 

@object_widget_adapter(schemata.IPoint)
class PointEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-point.html'

@object_widget_adapter(schemata.IPoint)
class PointReadWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-point.html'

# ITemporalExtent

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-temporal_extent.html'

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentReadWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-temporal_extent.html'

# IPostalAddress

@object_widget_adapter(schemata.IPostalAddress)
class PostalAddressEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address.html'

@object_widget_adapter(schemata.IPostalAddress, qualifiers=['compact'])
class PostalAddressCompactEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address-compact.html'

@object_widget_adapter(schemata.IPostalAddress, qualifiers=['comfortable'])
class PostalAddressComfortableEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address-comfortable.html'

@object_widget_adapter(schemata.IPostalAddress)
class PostalAddressReadWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-postal_address.html'

# IContactInfo

@object_widget_adapter(schemata.IContactInfo)
class ContactInfoEditWidget(base_widgets.EditObjectWidget):

    def get_field_qualifiers(self):
        return {
            'email': 'email'
        }
    
    def get_template(self):
        return None # use glue template
        #return 'package/snippets/objects/edit-contact_info.html'

@object_widget_adapter(schemata.IContactInfo)
class ContactInfoReadWidget(base_widgets.ReadObjectWidget):
    
    def get_field_qualifiers(self):
        return {
            'email': 'email'
        }

    def get_template(self):
        return None # use glue template
        #return 'package/snippets/objects/read-contact_info.html'

# IFoo

@object_widget_adapter(schemata.IFoo)
class FooEditWidget(base_widgets.EditObjectWidget):

    def prepare_template_vars(self, name_prefix, data):
        data = base_widgets.EditObjectWidget.prepare_template_vars(self, name_prefix, data)
        return data
    
    def get_omitted_fields(self):
        return ['geometry']
    
    def get_field_qualifiers(self):
        return {
        }
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-edit-foo.html'
        
    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IFoo)
class FooReadWidget(base_widgets.ReadObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        data = base_widgets.ReadObjectWidget.prepare_template_vars(self, name_prefix, data)
        return data
    
    def get_omitted_fields(self):
        return ['geometry']
   
    def get_field_qualifiers(self):
        return {
        }
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-foo.html'

    def get_template(self):
        return None # use glue template

