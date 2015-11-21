# -*- encoding: utf-8 -*-

import zope.interface
import dictdiffer
import copy
import json
import pylons

from nose.tools import istest, nottest, raises
from nose.plugins.skip import SkipTest

import ckan
from ckan.plugins import toolkit
from ckan.tests import CreateTestData 

from ckanext.publicamundi.lib.util import check_uuid
from ckanext.publicamundi.lib import dictization
from ckanext.publicamundi.lib.metadata import (
    factory_for_metadata, class_for_metadata, FieldContext)
from ckanext.publicamundi.lib.metadata import translator_for
from ckanext.publicamundi.lib.metadata.i18n import *
from ckanext.publicamundi.tests.helpers import make_api_context

class TestController(ckan.tests.TestController):

    request_headers = {
        'Content-Type': 'application/json',
    }

    request_environ = {
        'REMOTE_USER': 'tester',
    }
    
    packages = {
        'foo': [
            ('el', {'en'}, 'hello-foo-1', { 
                'title': u'Καλημέρα Foo (1)',
                'name': 'hello-foo-1',
                'notes': u'Τρα λαλα λαλλαλαλαλα!',
                'author': u'Κανένας',
                'license_id': 'notspecified',
                'version': '1.0.1a',
                'maintainer': u'Nowhere Man',
                'author_email': 'nowhere-man@example.com',
                'maintainer_email': 'nowhere-man@example.com',
                'tags': [ 
                    {'name': 'hello-world', 'display_name': 'Hello World'}, 
                    {'name': u'test', 'display_name': 'Test'},],
                'dataset_type': 'foo',
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
            }),
            ('en', {'el'}, 'hello-foo-2', { 
                'title': u'Hello Foo (2)',
                'name': 'hello-foo-2',
                'notes': u'Yupi ya ya!',
                'author': u'Nowhere Man',
                'license_id': 'notspecified',
                'version': '1.0.3c',
                'maintainer': u'Nowhere Man',
                'author_email': 'nowhere-man@example.com',
                'maintainer_email': 'nowhere-man@example.com',
                'tags': [ 
                    {'name': 'hello-world', 'display_name': 'Hello World'}, 
                    {'name': u'test', 'display_name': 'Test'},],
                'dataset_type': 'foo',
                'foo': {
                    'baz': u'BaoBab',
                    'title': u'Hello Foo (2)',
                    'description': u'Yupi ya ya, yupi yupi ya',
                    'rating': 9,
                    'grade': 5.00,
                    'reviewed': False,
                    'created': u'2014-09-13T17:00:00',
                    'temporal_extent': {'start': '2012-01-01', 'end': '2013-01-01'},
                    'thematic_category': 'health',
                },
            }),
        ],
        'inspire': [
            # Todo
        ],
    }

    translatable_fields = {
        'foo': [],
        'inspire': []
    }
   
    default_lang = None

    @classmethod
    def setup_class(cls):
        CreateTestData.create_user('tester', about='A tester', password='tester')
        cls.find_translatable_fields()
        cls.default_lang = pylons.config['ckan.locale_default']

    @classmethod
    def teardown_class(cls):
        pass

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
                yield self._test_1, dtype, i, name, source_lang, langs
    
    @staticmethod
    def _check_if_changed(d1, d2, expected_keys={}):
        d1f = dictization.flatten(d1)
        d2f = dictization.flatten(d1)
        for k in (set(d1f.keys()) - set(expected_keys)):
            assert d1f[k] == d2f[k], 'Expected not to be changed!'
    
    def _test_1(self, dtype, i, name, source_lang, langs):
        data = self.packages[dtype][i][-1]

        req_opts = {
            'headers': self.request_headers,
            'extra_environ': self.request_environ,
            'status': '*',
        }

        # Create 2 versions from this data dict: 
        #  1. with explicit language
        #  2. without language, will assume default CKAN locale  
        
        data1 = copy.deepcopy(data)
        data1['name'] = data1['name'] + "-" + source_lang
        data1['language'] = source_lang
       
        data2 = copy.deepcopy(data)
        data2['name'] = data2['name'] + "-xx" 
        data2.pop('language', None)

        for source_lang_expected, dat in [
                (source_lang, data1), 
                (self.default_lang, data2)
            ]:

            # Create 

            resp = self.app.post('/api/action/dataset_create', json.dumps(dat), **req_opts)
            assert resp and (resp.status in [200, 201]) and resp.json
            assert resp.json.get('success') and resp.json.get('result')
            assert resp.json['result']['language'] == source_lang_expected
            assert not 'translated_to_language' in resp.json['result'], 'edit action!'
            assert 'identifier' in resp.json['result'][dtype]

            # Read in (expected) source language

            q = {'id': dat['name'], 'lang': source_lang_expected}
            resp = self.app.get('/api/action/dataset_show', q, **req_opts)
            assert resp and (resp.status in [200, 201]) and resp.json
            assert resp.json.get('success') and resp.json.get('result')
            assert resp.json['result']['language'] == source_lang_expected 
            assert not 'translated_to_language' in resp.json['result'], 'no need to translate!'
            assert 'identifier' in resp.json['result'][dtype]
            self._check_if_changed(dat[dtype], resp.json['result'][dtype])

            # Read in other languages

            for lang in ((langs | {source_lang}) - {source_lang_expected}):
                q = {'id': dat['name'], 'lang': lang}
                resp = self.app.get('/api/action/dataset_show', q, **req_opts)
                assert resp and (resp.status in [200, 201]) and resp.json
                assert resp.json.get('success') and resp.json.get('result')
                assert resp.json['result']['language'] == source_lang_expected
                assert resp.json['result']['translated_to_language'] == lang
                assert 'identifier' in resp.json['result'][dtype]
                self._check_if_changed(dat[dtype], resp.json['result'][dtype])
            
            # Now, translate a few textual fields

            # Todo

            # Re-read in (expected) source language

            # Todo

            # Re-read in other languages

            # Todo


