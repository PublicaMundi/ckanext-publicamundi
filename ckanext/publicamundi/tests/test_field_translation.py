# -*- encoding: utf-8 -*-

import zope.interface
import zope.schema
from zope.interface.verify import verifyObject, verifyClass
import copy
import json

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

    packages = fixtures.packages['ckan']

    @classmethod
    def setup_class(cls):
        
        # Note Testing package-scoped translation requires some existing datasets

        CreateTestData.create_user('tester', about='A tester', password='tester')
        for pkg in cls.packages:
            ctx = make_api_context('tester')
            pkg_result = create_action(ctx, pkg)
            pkg.update({'id': pkg_result['id']})
        
        return

    @classmethod
    def teardown_class(cls):
        pass

    def test_interfaces(self):
        
        # Test package_translation.* translators
        
        for pkg_id, source_language in [
                ('6b1d06b6-b1d3-4ba2-8e62-c5c410ed502a', 'en'), 
                ('6b1d06b6-b1d3-4ba2-8e62-c5c410ed502a', None)]:
            tr = package_translation.FieldTranslator(pkg_id, source_language)
            assert verifyObject(IKeyBasedFieldTranslator, tr)
            assert not zope.schema.getValidationErrors(IKeyBasedFieldTranslator, tr)
            assert (tr.source_language == source_language) or (not source_language)
            assert tr.package_id == pkg_id

        # Test term_translation.* field translators
        
        for text_domain in ['publicamundi', None]:
            tr = term_translation.FieldTranslator(text_domain)
            assert verifyObject(IValueBasedFieldTranslator, tr)
            assert not zope.schema.getValidationErrors(IValueBasedFieldTranslator, tr)

    def test_package_translation(self):
        
        for i, pkg in enumerate(self.packages):
            yield self._test_package_translation, i, 'el'

    def _test_package_translation(self, i, language):
        
        pkg = self.packages[i]
        tr = package_translation.FieldTranslator(pkg['id'], pkg['language'])
        
        # Discard existing translations for this package
        
        tr.discard()

        # Lookup for translations (nothing yet)

        for k in ['title', 'notes']:
            yf = zope.schema.Text().bind(FieldContext(key=(k,), value=pkg[k]))
            # Lookup for a translation (nothing yet)
            translated_yf = tr.get(yf, language) 
            assert translated_yf is None # no translation exists yet
            # Add translations
            translated_value = u' ** BEGIN TRANSLATION ** %s ** END TRANSLATION **' % (pkg[k])
            tr.translate(yf, translated_value, language)
            # Lookup again for translations (should be there)
            translated_yf = tr.get(yf, language) 
            assert translated_yf.context.value == translated_value 
        pass

    def test_term_translation(self):
        
        # Todo
        
        raise SkipTest('Term-based translation is not implemented yet!') 
