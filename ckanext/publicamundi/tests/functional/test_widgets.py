import zope.interface
import zope.schema
import logging
import nose.tools
import pyquery

import pylons
import ckan.tests
from ckan.tests import url_for

from ckanext.publicamundi.tests.functional import with_request_context
from ckanext.publicamundi.tests import fixtures

from ckanext.publicamundi.lib.metadata import adapter_registry 
from ckanext.publicamundi.lib.metadata.schemata import *
from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import ibase as ibase_widgets
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets import markup_for_field, markup_for_object
from ckanext.publicamundi.lib.metadata.widgets import field_widget_adapter

log1 = logging.getLogger(__name__)

## Define widgets ##

@field_widget_adapter(zope.schema.interfaces.IBool, qualifiers=['checkbox1'])
class BoolWidget1(base_widgets.EditFieldWidget):
    
    def get_template(self):
        return 'package/snippets/fields/edit-checkbox-1.html'

@field_widget_adapter(zope.schema.interfaces.IBool, qualifiers=['checkbox2'])
class BoolWidget2(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-checkbox-2.html'

BoolWidget3 = type('BoolWidget3', (base_widgets.EditFieldWidget,), {
    'get_template': None
})
BoolWidget3.get_template = lambda t: 'package/snippets/fields/edit-checkbox-3.html'
BoolWidget3 = \
    field_widget_adapter(zope.schema.interfaces.IBool, qualifiers=['checkbox3'])\
    (BoolWidget3)

## Tests ##

class TestController(ckan.tests.TestController):

    ## Test fields ##
 
    @nose.tools.istest
    def test_registered_field_widgets(self):
        field_ifaces = [
            zope.schema.interfaces.IBool,
            zope.schema.interfaces.IChoice,
            zope.schema.interfaces.IText,
            zope.schema.interfaces.ITextLine,
            zope.schema.interfaces.IList,
            zope.schema.interfaces.IDict,
            zope.schema.interfaces.IObject,
        ]
        for iface in field_ifaces:
            yield self._test_registered_field_widgets, iface
    
    def _test_registered_field_widgets(self, field_iface):
        '''Fetch all registered adapters for a given field interface'''
        adapters = adapter_registry.lookupAll([field_iface], ibase_widgets.IFieldWidget)
        print
        print ' -- Registered widget adapters for field %s -- ' %(field_iface)
        for adapter in adapters:
            print adapter
        assert len(adapters) >= 2  
    
    @nose.tools.istest
    def test_read_field_widgets(self):
        '''Generate markup for reading fields'''
        for k in ['title', 'reviewed']:
            yield self._test_markup_for_field, 'foo1', k, 'read'
            yield self._test_markup_for_field, 'foo1', k, 'read', { 'title': u'X1' }

    @nose.tools.istest
    def test_edit_field_widgets(self):
        '''Generate markup for editing fields'''
        for k in ['title', 'reviewed', 'notes', 'thematic_category', 'wakeup_time', 'created']:
            yield self._test_markup_for_field, 'foo1', k, 'edit'
            yield self._test_markup_for_field, 'foo1', k, 'edit', { 'title': u'Another Title' }
            yield self._test_markup_for_field, 'foo1', k, 'edit', { 'required': False }
        for k in ['reviewed']:
            yield self._test_markup_for_field, 'foo1', k, 'edit:checkbox_1'
            yield self._test_markup_for_field, 'foo1', k, 'edit:checkbox_2'
            yield self._test_markup_for_field, 'foo1', k, 'edit:checkbox_3'
            yield self._test_markup_for_field, 'foo1', k, 'edit:checkbox_3.bar.baz'

    @with_request_context('publicamundi-tests', 'index')
    def _test_markup_for_field(self, fixture_name, k, action, data={}):
        '''Render a field widget'''
        action = action.split(':')[0]
        x = getattr(fixtures, fixture_name)
        f = x.get_field(k)
        markup = markup_for_field(action, f, fixture_name, data)
        log1.info('Generated %s markup for %r:\n%s' %(action, f, markup))
        assert markup
        pq = pyquery.PyQuery(unicode(markup))
        assert pq
        assert pq.is_('div')
        assert pq.is_('.field-qname-%s\\.%s' %(fixture_name, k))
        assert pq.is_('.field-%s-widget' %(action))
        if action.startswith('edit'):
            e = pq.find('input') or pq.find('textarea') or pq.find('select')
            assert e
            assert e.attr('name') == '%s.%s' %(fixture_name, k)
            assert e.attr('id') == 'input-%s.%s' %(fixture_name, k)


    ## Test objects ##
    
    @nose.tools.istest
    def test_registered_object_widgets(self):
        object_ifaces = [
            IPoint,
            ITemporalExtent,
        ]
        for iface in object_ifaces:
            yield self._test_registered_object_widgets, iface
    
    def _test_registered_object_widgets(self, object_iface):
        '''Fetch all registered adapters for a given object interface'''
        adapters = adapter_registry.lookupAll([object_iface], ibase_widgets.IObjectWidget)
        print
        print ' -- Registered widget adapters for schema %s -- ' %(object_iface)
        for adapter in adapters:
            print adapter
        assert len(adapters) >= 2  

    @nose.tools.istest
    def test_read_object_widgets(self):
        '''Generate markup for reading objects'''
        yield self._test_markup_for_object, 'pt1', 'read'
        yield self._test_markup_for_object, 'pt1', 'read', { 'title': u'Point #1' }

    @nose.tools.istest
    def test_edit_object_widgets(self):
        '''Generate markup for writing objects'''
        yield self._test_markup_for_object, 'pt1', 'edit'
        yield self._test_markup_for_object, 'pt1', 'edit', { 'title': u'Point #1' }

    @with_request_context('publicamundi-tests', 'index')
    def _test_markup_for_object(self, fixture_name, action, data={}):
        '''Render an object widget'''
        obj = getattr(fixtures, fixture_name)
        markup = markup_for_object(action, obj, fixture_name, data)
        log1.info('Generated %s markup for object %r:\n%s' %(action, obj, markup))
        assert markup
        pq = pyquery.PyQuery(unicode(markup))
        assert pq
        assert pq.is_('div')

