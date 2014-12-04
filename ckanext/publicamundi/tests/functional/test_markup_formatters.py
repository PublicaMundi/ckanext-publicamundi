import nose.tools
import zope.interface
from zope.interface.verify import verifyObject

from ckan.tests import TestController as BaseTestController
from ckanext.publicamundi.tests.functional import with_request_context

from ckanext.publicamundi.tests.helpers import assert_faulty_keys
from ckanext.publicamundi.tests import fixtures

from ckanext.publicamundi.lib.metadata import formatters
from ckanext.publicamundi.lib.metadata import (
    formatter_for_field, formatter_for_object, IFormatter)


# Tests

class TestController(BaseTestController):
    
    @nose.tools.istest
    def test_fields(self):
        yield self._test_field, 'foo1', 'temporal_extent'
        yield self._test_field, 'inspire1', 'spatial_resolution'
    
    @nose.tools.istest
    def test_objects(self):
        yield self._test_object, 'bbox1'
        yield self._test_object, 'contact1'
        yield self._test_object, 'spatialres1'
    
    @with_request_context('publicamundi-tests', 'index')
    def _test_object(self, fixture_name):
        obj = getattr(fixtures, fixture_name)
        s = format(obj, 'markup')
        s = format(obj, 'markup:q=baobab')

    @with_request_context('publicamundi-tests', 'index')
    def _test_field(self, fixture_name, field_name):
        obj = getattr(fixtures, fixture_name)
        field = obj.get_field(field_name)
        formatter = formatter_for_field(field, 'markup')
        verifyObject(IFormatter, formatter) 
        s = formatter.format()
        print ' -- format:markup %s -- ' %(type(field))
        print s

        
