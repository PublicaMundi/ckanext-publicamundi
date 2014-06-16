import logging
import pylons

import ckan.tests
from ckan.tests import url_for

from ckanext.publicamundi.tests.functional import with_request_context
from ckanext.publicamundi.tests.fixtures import x1

from ckanext.publicamundi.lib.metadata.types import *
from ckanext.publicamundi.lib.metadata.widgets import generate_markup_for_field

log1 = logging.getLogger(__name__)
log1.setLevel(logging.INFO)

class TestController(ckan.tests.TestController):

    def _test_integer(self, i):
        assert isinstance(i, int)

    def test_integers(self):
        for i in [3, 5, 'a']:
            yield self._test_integer, i

    @with_request_context('publicamundi-tests', action='index')
    def test_render_field_widget(self):
        '''Render a field widget'''
        k = 'title'
        S = x1.get_schema()
        F = S.get(k)
        f = F.get(x1)
        markup = generate_markup_for_field('read', F, f, 'x1')
        log1.info('Got markup %s' %(markup))
        assert markup

