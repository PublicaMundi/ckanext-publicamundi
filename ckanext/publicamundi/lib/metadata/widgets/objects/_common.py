import itertools
import zope.interface

from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from ckanext.publicamundi.lib.metadata.widgets.base import (
    ReadObjectWidget, EditObjectWidget,
    ReadFieldWidget, EditFieldWidget)

#
# IObject - Tabular views
#

@object_widget_adapter(schemata.IObject, qualifiers=['table'])
class TableObjectReadWidget(ReadObjectWidget):

    max_depth = 2
    
    def get_template(self):
        return 'package/snippets/objects/read-object-table.html'

    def prepare_template_vars(self, name_prefix, data):
        cls = type(self)
        tpl_vars = super(cls, self).prepare_template_vars(name_prefix, data)

        # Preprocess self.obj to be displayed as table rows
        
        max_depth = data.get('max_depth', 0) or self.max_depth

        obj_dict = self.obj.to_dict(flat=False, opts={ 
            'max-depth': max_depth,
            'format-values': 'default', })
        
        num_rows, num_cols, rows = cls._tabulate(obj_dict)
       
        # Provide human-friendly names for TH elements 
        
        for row in rows:
            for th in filter(lambda t: t.tag == 'th', row):
                kp = th.key_path()
                field = self.obj.get_field(kp)
                th.title = field.context.title or field.title
                
        # Provide vars to template

        tpl_vars.update({
            'obj_dict': obj_dict,
            'rows': rows,
            'num_rows': num_rows,
            'num_cols': num_cols,
        })
        
        return tpl_vars

    # Helpers

    class _Td(object):

        __slots__ = ('parent', 'data', 'rowspan', 'colspan')

        tag = 'td'
        
        def  __init__(self, data, rowspan=1, colspan=1):
            self.data = data
            self.rowspan = rowspan
            self.colspan = colspan
            self.parent = None

        def __repr__(self):
            return '%s(data=%r, rowspan=%s, colspan=%s)' % (
                self.tag.upper(), 
                self.data, self.rowspan, self.colspan)
        
    class _Th(_Td):
        
        __slots__ = ('title',)

        tag = 'th'
        
        def  __init__(self, data, rowspan=1, colspan=1):
            super(type(self), self).__init__(data, rowspan, colspan)
            self.title = self.data

        def key(self):
            return self.data
        
        def key_path(self):
            p = self
            path = [p.data]
            while p.parent:
                path.insert(0, p.parent.data)
                p = p.parent
            return tuple(path)
       
    @classmethod
    def _tabulate(cls, d):
        
        rows = cls._tabulate_rows(d)
        num_rows = len(rows)
        num_cols = max(map(len, rows))

        for row in rows:
            row[-1].colspan += num_cols - len(row)
        
        return num_rows, num_cols, rows
    
    @classmethod 
    def _tabulate_rows(cls, x):
        
        Td, Th = cls._Td, cls._Th
        
        itr = None
        if isinstance(x, dict):
            itr = x.iteritems()
        elif isinstance(x, list):
            itr = enumerate(x)
        
        res = list()
        if itr:
            for key, val in itr:
                rows = cls._tabulate_rows(val)
                nr = len(rows)
                if rows:
                    parent = Th(data=key, rowspan=nr, colspan=1)
                    # Prepend row grouper to 1st row
                    rows[0].insert(0, parent)
                    rows[0][1].parent = parent
                    # Update all successive (#>1) rows
                    for i in range(1, nr):
                        row = rows[i]
                        if not row[0].parent: 
                            row[0].parent = parent
                        row[-1].colspan -= 1
                    res.extend(rows)
        else:
            if x:
                res.append([Td(data=unicode(x), colspan=1)])
        
        return res

#
# IPoint
#

@object_widget_adapter(schemata.IPoint)
class PointEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-point.html'

@object_widget_adapter(schemata.IPoint)
class PointReadWidget(ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-point.html'

#
# ITemporalExtent
#

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-temporal_extent.html'

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentReadWidget(ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-temporal_extent.html'

#
# IPostalAddress
#

@object_widget_adapter(schemata.IPostalAddress)
class PostalAddressEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address.html'

@object_widget_adapter(schemata.IPostalAddress, qualifiers=['compact'])
class PostalAddressCompactEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address-compact.html'

@object_widget_adapter(schemata.IPostalAddress, qualifiers=['comfortable'])
class PostalAddressComfortableEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address-comfortable.html'

@object_widget_adapter(schemata.IPostalAddress)
class PostalAddressReadWidget(ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-postal_address.html'

#
# IContactInfo
#

@object_widget_adapter(schemata.IContactInfo)
class ContactInfoEditWidget(EditObjectWidget):

    def get_field_qualifiers(self):
        return {
            'address': 'compact',
            'email': 'email'
        }
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-edit-contact_info.html'
        
    def get_template(self):
        return None # use glue template
        #return 'package/snippets/objects/edit-contact_info.html'

@object_widget_adapter(schemata.IContactInfo)
class ContactInfoReadWidget(ReadObjectWidget):
    
    def get_field_qualifiers(self):
        return {
            'email': 'email'
        }

    def get_template(self):
        return None # use glue template
        #return 'package/snippets/objects/read-contact_info.html'

