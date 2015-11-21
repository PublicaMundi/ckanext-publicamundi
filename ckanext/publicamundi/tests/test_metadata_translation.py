# -*- encoding: utf-8 -*-

import zope.interface
import zope.schema
import dictdiffer

from nose.tools import istest, nottest, raises
from nose.plugins.skip import SkipTest

import ckan
from ckan.plugins import toolkit
from ckan.tests import CreateTestData 

from ckanext.publicamundi.lib.util import check_uuid
from ckanext.publicamundi.lib.metadata import (
    factory_for_metadata, class_for_metadata, FieldContext)
from ckanext.publicamundi.lib.metadata import translator_for
from ckanext.publicamundi.lib.metadata.i18n import *

from . import MockTmplContext, MockRequest
from .helpers import make_api_context

create_action = toolkit.get_action('package_create')

toolkit.c = MockTmplContext()
toolkit.request = MockRequest()

class TestController(ckan.tests.TestController):
 
    packages = {
        'foo': [
            ('el', ['en'], 'hello-foo-1', { 
                'title': u'Καλημέρα Foo (1)',
                'name': 'hello-foo-1',
                'notes': u'Τρα λαλα λαλλαλαλαλα!',
                'author': u'Κανένας',
                'license_id': 'notspecified',
                'version': '1.0.1b',
                'maintainer': u'Nowhere Man',
                'author_email': 'nowhere-man@example.com',
                'maintainer_email': 'nowhere-man@example.com',
                'tags': [ 
                    {'name': 'hello-world', 'display_name': 'Hello World'}, 
                    {'name': u'test', 'display_name': 'Test'},],
                'dataset_type': 'foo',
                'language': 'el',
                'foo': {
                    'baz': u'BaoBab',
                    'title': u'Καλημέρα Φου (1)',
                    'description': u'Τριαλαριλαρο',
                    'rating': 9,
                    'grade': 5.12,
                    'reviewed': False,
                    'created': u'2014-09-13T17:00:00',
                    'temporal_extent': {'start': '2012-01-01', 'end': '2013-01-01'},
                    'thematic_category': 'health',
                },
            })
        ]
    }

    translatable_fields = {
        'foo': [],
    }

    @classmethod
    def setup_class(cls):
        cls.create_packages()
        cls.find_translatable_fields()
    
    @classmethod
    def teardown_class(cls):
        pass

    @classmethod
    def create_packages(cls):
        CreateTestData.create_user('tester', about='A tester', password='tester')
        for dtype, packages in cls.packages.items(): 
            for source_lang, langs, name, pkg in packages:
                ctx = make_api_context('tester')
                pkg_result = create_action(ctx, pkg)
                pkg['id'] = pkg_result['id']
                pkg[dtype]['identifier'] = pkg_result[dtype].identifier
        return

    @classmethod
    def find_translatable_fields(cls):
        for dtype in cls.packages:
            md_cls = class_for_metadata(dtype)
            flattened_fields = md_cls.get_flattened_fields()
            for kp, uf in flattened_fields.items():
                if uf.queryTaggedValue('translatable'):
                    cls.translatable_fields[dtype].append(kp)

    @istest
    def test_1(self):
        
        for dtype, packages in self.packages.items():
            for i, (source_lang, langs, name, pkg) in enumerate(packages):
                for lang in langs:
                    yield self._test_1, dtype, i, name, source_lang, lang

    def _test_1(self, dtype, i, name, source_lang, lang):
       
        pkg = self.packages[dtype][i][-1]
        md = factory_for_metadata(dtype)()
        md.from_dict(pkg[dtype], is_flat=0, opts={'unserialize-values': 1})
        assert md.identifier and check_uuid(md.identifier)
        
        translator = translator_for(md, source_lang)
        assert translator
        assert IMetadataTranslator in zope.interface.providedBy(translator)
        
        # Read a translated view
        
        md_1 = translator.get(lang)
        assert md_1 and isinstance(md_1, type(md))
        assert ITranslatedMetadata in zope.interface.providedBy(md_1)
        assert md_1 == md, 'Nothing is translated yet, should be identical'  

        # Tranlate a few fields
        
        field_translator = translator.get_field_translators()[0]
        
        translations = {} 
        for key in self.translatable_fields[dtype]:
            yf = md.get_field(key)
            translations[key] = ' ** TRANSLATE ** ' + yf.context.value
            yf.context.key = (dtype,) + key
            field_translator.translate(yf, translations[key], lang)            

        # Re-read a translated view
        
        md_2 = translator.get(lang)
        assert md_2 and isinstance(md_2, type(md))
        assert ITranslatedMetadata in zope.interface.providedBy(md_2)
        assert md_2 != md, 'Some fields should be translated'  
        
        changes = list(dictdiffer.diff(md.to_dict(), md_2.to_dict())) 
        translated_keys = set(translations.keys())
        assert len(changes) > 0
        for changetype, skey, (changed_from, changed_to) in changes:
            assert changetype == 'change'
            key = tuple(skey.split('.'))
            assert key in translations
            assert translations[key] == changed_to
            yf0, yf2 = md.get_field(key), md_2.get_field(key)
            assert yf0.context.value == changed_from 
            assert yf2.context.value == changed_to 
            assert key in translated_keys
            translated_keys.remove(key)
        assert not translated_keys, 'All keys should be consumed'
        
        pass

