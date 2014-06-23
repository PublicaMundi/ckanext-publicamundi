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
from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import markup_for_field
from ckanext.publicamundi.lib.metadata.widgets import markup_for_object
from ckanext.publicamundi.lib.metadata.widgets import ibase as ibase_widgets
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets

log1 = logging.getLogger(__name__)

## Define widgets ##

class BoolWidget1(base_widgets.EditFieldWidget):
    action = 'edit.checkbox-1'
    def get_template(self):
        return 'package/snippets/fields/edit-checkbox-1.html'

class BoolWidget2(base_widgets.EditFieldWidget):
    action = 'edit.checkbox-2'
    def get_template(self):
        return 'package/snippets/fields/edit-checkbox-2.html'

BoolWidget3 = type('BoolWidget3', (base_widgets.EditFieldWidget,), {
    'action': None,
    'get_template': None
})
BoolWidget3.action = 'edit.checkbox-3'
BoolWidget3.get_template = lambda t: 'package/snippets/fields/edit-checkbox-3.html'

field_widgets.register_field_widget(zope.schema.interfaces.IBool, BoolWidget1)
field_widgets.register_field_widget(zope.schema.interfaces.IBool, BoolWidget2)
field_widgets.register_field_widget(zope.schema.interfaces.IBool, BoolWidget3)

## Tests ##

class TestController(ckan.tests.TestController):

    ## Test fields ##

    @nose.tools.istest
    def test_registered_field_widgets(self):
        field_ifaces = [
            zope.schema.interfaces.IBool,
            zope.schema.interfaces.IText,
            zope.schema.interfaces.IList,
        ]
        for iface in field_ifaces:
            yield self._test_registered_field_widgets, iface
    
    def _test_registered_field_widgets(self, field_iface):
        adapters = adapter_registry.lookupAll([field_iface], ibase_widgets.IFieldWidget)
        print
        print ' -- Widget adapters for field %s -- ' %(field_iface)
        for adapter in adapters:
            print adapter
        assert len(adapters) > 1
 
    @nose.tools.istest
    def test_read_field_widgets(self):
        '''Generate markup for reading fields'''
        for k in ['title', 'reviewed']:
            yield self._test_markup_for_field, 'foo1', k, 'read'
            yield self._test_markup_for_field, 'foo1', k, 'read', { 'title': u'X1' }

    @nose.tools.istest
    def test_edit_field_widgets(self):
        '''Generate markup for editing fields'''
        for k in ['title', 'reviewed', 'notes', 'thematic_category']:
            yield self._test_markup_for_field, 'foo1', k, 'edit'
            yield self._test_markup_for_field, 'foo1', k, 'edit', { 'title': u'Another Title' }
            yield self._test_markup_for_field, 'foo1', k, 'edit', { 'required': False }
        for k in ['reviewed']:
            yield self._test_markup_for_field, 'foo1', k, 'edit.checkbox-1'
            yield self._test_markup_for_field, 'foo1', k, 'edit.checkbox-2'
            yield self._test_markup_for_field, 'foo1', k, 'edit.checkbox-3'

    @with_request_context('publicamundi-tests', 'index')
    def _test_markup_for_field(self, fixture_name, k, action, data={}):
        '''Render a field widget'''
        base_action = action.split('.')[0]
        x = getattr(fixtures, fixture_name)
        f = x.get_field(k)
        markup = markup_for_field(action, f, fixture_name, data)
        log1.info('Generated %s markup for %r:\n%s' %(action, f, markup))
        assert markup
        pq = pyquery.PyQuery(unicode(markup))
        assert pq
        assert pq.is_('div')
        assert pq.is_('.field-%s-%s\\.%s' %(base_action, fixture_name, k))
        if action.startswith('edit'):
            e = pq.find('input') or pq.find('textarea') or pq.find('select')
            assert e
            assert e.attr('name') == '%s.%s' %(fixture_name, k)


    ## Test objects ##

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

