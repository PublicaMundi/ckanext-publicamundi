import logging
import pylons

import ckan.tests
from ckan.tests import url_for

from ckanext.publicamundi.tests.functional import with_request_context
from ckanext.publicamundi.tests import fixtures

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import generate_markup_for_field

log1 = logging.getLogger(__name__)
log1.setLevel(logging.INFO)

class TestController(ckan.tests.TestController):

    def test_read_field_widgets(self):
        '''Generate markup for reading fields'''
        for k in ['title']:
            yield self._test_markup_for_field, 'x1', k, 'read'

    @with_request_context('publicamundi-tests', 'index')
    def _test_markup_for_field(self, fixture_name, k, action):
        '''Render a field widget'''
        x = getattr(fixtures, fixture_name)
        S = x.get_schema()
        F = S.get(k)
        f = F.get(x)
        markup = generate_markup_for_field(action, F, f, fixture_name)
        log1.info('Generated markup for %r: %s' %(x, markup))
        assert markup

