import itertools
import zope.interface
from collections import namedtuple
from itertools import groupby

from ckanext.publicamundi.lib.metadata import schemata
from ckanext.publicamundi.lib.metadata.widgets import object_widget_adapter
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets

## IObject - Tabular views ##

@object_widget_adapter(schemata.IObject, qualifiers=['table'])
class ObjectAsTableReadWidget(base_widgets.ReadObjectWidget):

    max_depth = 3
    
    def get_template(self):
        return 'package/snippets/objects/read-object-table.html'

    def prepare_template_vars(self, name_prefix, data):
        cls = type(self)
        tpl_vars = super(cls, self).prepare_template_vars(name_prefix, data)

        # Preprocess self.obj to be displayed as table rows
        
        max_depth = self.max_depth

        obj_dict = self.obj.to_dict(flat=False, opts={ 
            'max-depth': max_depth,
            'format-values': 'default', })
        
        num_rows, num_cols, rows = cls._tabulate(obj_dict)
       
        # Replace keys (in TH elements) with human-friendly titles
        
        for row in rows:
            for t in filter(lambda t: t.tag == 'th', row):
                kp = t.key_path()
                field = self.obj.get_field(kp, bind=False)
                if field.title:
                    k = t.key()
                    if isinstance(k, int):
                        t.title = u'%s #%d' %(field.title, k)
                    else:
                        t.title = field.title
                
        # Provide vars to template

        tpl_vars.update({
            'obj_dict': obj_dict,
            'rows': rows,
            'num_rows': num_rows,
            'num_cols': num_cols,
        })
        
        return tpl_vars

    # Helpers

    class _td(object):

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
        
    class _th(_td):
        
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
        
        td, th = cls._td, cls._th
        
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
                    parent = th(data=key, rowspan=nr, colspan=1)
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
                res.append([td(data=unicode(x), colspan=1)])
        
        return res

## IPoint ##

@object_widget_adapter(schemata.IPoint)
class PointEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-point.html'

@object_widget_adapter(schemata.IPoint)
class PointReadWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-point.html'

## ITemporalExtent ##

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentEditWidget(base_widgets.EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-temporal_extent.html'

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentReadWidget(base_widgets.ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-temporal_extent.html'

## IPostalAddress ##

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

## IContactInfo ##

@object_widget_adapter(schemata.IContactInfo)
class ContactInfoEditWidget(base_widgets.EditObjectWidget):

    def get_field_qualifiers(self):
        return {
            'address': 'comfortable',
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

