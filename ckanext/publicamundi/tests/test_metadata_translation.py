# -*- encoding: utf-8 -*-

import zope.interface
import zope.schema
from zope.interface.verify import verifyObject, verifyClass

from nose.tools import istest, nottest, raises
from nose.plugins.skip import SkipTest

import ckan
from ckan.plugins import toolkit
from ckan.tests import CreateTestData 

from ckanext.publicamundi.lib.metadata import FieldContext
from ckanext.publicamundi.lib.metadata.i18n import *

from . import MockTmplContext, MockRequest
from . import fixtures
from .helpers import make_api_context

create_action = toolkit.get_action('package_create')

toolkit.c = MockTmplContext()
toolkit.request = MockRequest()

class TestController(ckan.tests.TestController):
    
    packages = fixtures.packages['foo']
    foos = None

    @classmethod
    def setup_class(cls):

        CreateTestData.create_user('tester', about='A tester', password='tester')
        cls.foos = []
        for pkg in cls.packages:
            ctx = make_api_context('tester')
            pkg_result = create_action(ctx, pkg)
            pkg.update({'id': pkg_result['id']})
            cls.foos.append(pkg_result['foo'])
        
        return

    @classmethod
    def teardown_class(cls):
        pass

    @istest
    def test_translate_foo(self):
        for i in range(0, len(self.foos)):
            yield self._test_translate_foo, i, self.packages[i]['id']

    def _test_translate_foo(self, i, *args):
        foo = self.foos[i]
        assert False
