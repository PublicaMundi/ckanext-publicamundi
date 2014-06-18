import logging
import nose.tools
import pyquery

import pylons
import ckan.tests
from ckan.tests import url_for

from ckanext.publicamundi.tests.functional import with_request_context
from ckanext.publicamundi.tests import fixtures

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import generate_markup_for_field
from ckanext.publicamundi.lib.metadata.widgets import generate_markup_for_object

log1 = logging.getLogger(__name__)
#log1.setLevel(logging.INFO)

class TestController(ckan.tests.TestController):

    ## Fields ##

    @nose.tools.istest
    def test_read_field_widgets(self):
        '''Generate markup for reading fields'''
        for k in ['title']:
            yield self._test_markup_for_field, 'x1', k, 'read'
            yield self._test_markup_for_field, 'x1', k, 'read', { 'title': u'X1' }

    @nose.tools.istest
    def test_edit_field_widgets(self):
        '''Generate markup for editing fields'''
        for k in ['title']:
            yield self._test_markup_for_field, 'x1', k, 'edit'
            yield self._test_markup_for_field, 'x1', k, 'edit', { 'title': u'X1' }
            yield self._test_markup_for_field, 'x1', k, 'edit', { 'required': False }
            yield self._test_markup_for_field, 'x1', k, 'edit', { 'classes': [ 'control-large' ], 'title': u'Foo' }

    @with_request_context('publicamundi-tests', 'index')
    def _test_markup_for_field(self, fixture_name, k, action, data={}):
        '''Render a field widget'''
        x = getattr(fixtures, fixture_name)
        S = x.get_schema()
        F = S.get(k)
        f = F.get(x)
        markup = generate_markup_for_field(action, F, f, fixture_name, **data)
        log1.info('Generated %s markup for %r:\n%s' %(action, f, markup))
        assert markup
        pq = pyquery.PyQuery(unicode(markup))
        assert pq
        assert pq.is_('div')

    ## Objects ##

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
        markup = generate_markup_for_object(action, obj, fixture_name, **data)
        log1.info('Generated %s markup for object %r:\n%s' %(action, obj, markup))
        assert markup
        pq = pyquery.PyQuery(unicode(markup))
        assert pq
        assert pq.is_('div')


