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
class ContactInfoExtentEditWidget(base_widgets.EditObjectWidget):

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

