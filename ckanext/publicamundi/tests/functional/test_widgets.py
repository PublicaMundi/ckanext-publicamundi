import zope.interface
import zope.schema
import z3c.schema.email
import logging
import nose.tools
import pyquery

import pylons
import ckan.tests
from ckan.tests import url_for
from ckan.tests import TestController as BaseTestController

from ckanext.publicamundi.tests.functional import with_request_context
from ckanext.publicamundi.tests import fixtures

from ckanext.publicamundi.lib.metadata import (
    adapter_registry, Object, FieldContext)
from ckanext.publicamundi.lib.metadata.schemata import *
from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.widgets import ibase as ibase_widgets
from ckanext.publicamundi.lib.metadata.widgets import base as base_widgets
from ckanext.publicamundi.lib.metadata.widgets import fields as field_widgets
from ckanext.publicamundi.lib.metadata.widgets import (
    markup_for_field, markup_for_object, widget_for_object, widget_for_field)
from ckanext.publicamundi.lib.metadata.widgets import (
    field_widget_adapter, field_widget_multiadapter)

log1 = logging.getLogger(__name__)

#
# Define widgets
#

@field_widget_adapter(IBoolField, qualifiers=['checkbox1'])
class BoolWidget1(base_widgets.EditFieldWidget):
    
    def get_template(self):
        return 'package/snippets/fields/edit-bool-checkbox-1.html'

@field_widget_adapter(IBoolField, qualifiers=['checkbox2'])
class BoolWidget2(base_widgets.EditFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/edit-bool-checkbox-2.html'

BoolWidget3 = type('BoolWidget3', (base_widgets.EditFieldWidget,), {
    'get_template': None
})
BoolWidget3.get_template = lambda t: 'package/snippets/fields/edit-bool-checkbox-3.html'
BoolWidget3 = field_widget_adapter(IBoolField, qualifiers=['checkbox3'])(BoolWidget3)

class DummyImpl(NotImplementedError):
    pass

@field_widget_multiadapter([IListField, ITextLineField], qualifiers=['questions'])
class QuestionsWidget(field_widgets.ListEditWidget):
    
    def get_template(self):
        raise DummyImpl('This may be implemented')

@field_widget_multiadapter([IDictField, IContactInfo], qualifiers=['contacts'])
class ContactsWidget(field_widgets.DictEditWidget):
    
    def get_template(self):
        raise DummyImpl('This may be implemented')

#
# Tests
#

class TestController(BaseTestController):

    ## Test fields ##
    
    @nose.tools.istest
    def test_multiadapter(self):
        yield self._test_multiadapter
     
    @with_request_context('publicamundi-tests', 'index')
    def _test_multiadapter(self):
        '''Test multiadapters on collection-based fields'''
        
        # Adapt to (Dict, ContactInfo)

        field = fixtures.foo1.get_field(('contacts',))
        
        widget = widget_for_field('edit', field)
        print widget.render(name_prefix='test1', data={}) 
        
        widget = widget_for_field('edit:contacts', field)
        try:
            print widget.render(name_prefix='test1', data={}) 
        except DummyImpl:
            print '<dummy implementation for edit:contacts for %r>' %(field)
        else:
            assert False, 'This should have raised DummyImpl'

        # Adapt to (List, TextLine)
        
        field = zope.schema.List(
            title=u'Questions',
            value_type=zope.schema.TextLine(title=u'Question'),
        )
        field = field.bind(FieldContext(key='q', value=[u'when', u'where']))

        widget = widget_for_field('edit', field)
        print widget.render(name_prefix='test1', data={}) 
        
        widget = widget_for_field('edit:questions', field)
        try:
            print widget.render(name_prefix='test1', data={}) 
        except DummyImpl:
            print '<dummy implementation for edit:questions for %r>' %(field)
        else:
            assert False, 'This should have raised DummyImpl'
    
    @nose.tools.istest
    def test_registered_field_widgets(self):
        field_ifaces = [
            IBoolField,
            IChoiceField, ITextField, ITextLineField,
            IURIField,
            IEmailAddressField,
            IIntField, IFloatField,
            IDateField, IDatetimeField, ITimeField,
            IListField, IDictField, IObjectField,
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
        for k in ['title', 'reviewed', 'notes', 'thematic_category', 'wakeup_time', 'created', 'rating', 'grade', 'url']:
            yield self._test_markup_for_field, 'foo1', k, 'read'
            yield self._test_markup_for_field, 'foo1', k, 'read', { 'title': u'X1' }

    @nose.tools.istest
    def test_edit_field_widgets(self):
        '''Generate markup for editing fields'''
        for k in ['title', 'reviewed', 'notes', 'thematic_category', 'wakeup_time', 'created', 'rating', 'grade', 'url']:
            yield self._test_markup_for_field, 'foo1', k, 'edit'
            yield self._test_markup_for_field, 'foo1', k, 'edit', { 'title': u'Another Title' }
            yield self._test_markup_for_field, 'foo1', k, 'edit', { 'required': False }
        for k in ['reviewed']:
            yield self._test_markup_for_field, 'foo1', k, 'edit:checkbox_1'
            yield self._test_markup_for_field, 'foo1', k, 'edit:checkbox_2'
            yield self._test_markup_for_field, 'foo1', k, 'edit:checkbox_3'
            yield self._test_markup_for_field, 'foo1', k, 'edit:checkbox_3.bar.baz'
        for k in ['tags']:
            yield self._test_markup_for_field, 'foo1', k, 'edit:baz'
            yield self._test_markup_for_field, 'foo1', k, 'edit:tags'

    @with_request_context('publicamundi-tests', 'index')
    def _test_markup_for_field(self, fixture_name, k, action, data={}):
        '''Render a field widget'''
        action = action.split(':')[0]
        x = getattr(fixtures, fixture_name)
        f = x.get_field(k)
        errs = x.validate()
        errs = x.dictize_errors(errs)
        markup = markup_for_field(action, f,
            errors=errs, name_prefix=fixture_name, data=data)
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
            assert e.attr('name').startswith('%s.%s' %(fixture_name, k))
            assert e.attr('id').startswith('input-%s.%s' %(fixture_name, k))

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
        markup = markup_for_object(action, obj, name_prefix=fixture_name, data=data)
        log1.info('Generated %s markup for object %r:\n%s' %(action, obj, markup))
        assert markup
        pq = pyquery.PyQuery(unicode(markup))
        assert pq
        assert pq.is_('div')

