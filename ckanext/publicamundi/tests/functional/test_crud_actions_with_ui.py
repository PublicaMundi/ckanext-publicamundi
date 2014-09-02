import nose.tools

from ckan.tests import TestController as BaseTestController
from ckanext.publicamundi.tests.functional import with_request_context

from ckanext.publicamundi.lib.metadata.types.common import *
from ckanext.publicamundi.lib.metadata.base import *
from ckanext.publicamundi.tests import fixtures

# Tests

class TestController(BaseTestController):
    
    @with_request_context('publicamundi-tests', 'index')
    def test_create_dataset(self):
        pass

