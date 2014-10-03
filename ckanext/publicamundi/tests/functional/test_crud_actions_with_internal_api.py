# -*- encoding: utf-8 -*-

import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.tests.functional import with_request_context
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib import dictization

import nose.tools
import json
import collections
import copy
import ckan.tests
import pprint
#from ckan.tests import CreateTestData

from ckanext.publicamundi.lib.metadata import dataset_types, Object

class TestController(ckan.tests.TestController):

    core_keys = set([
        'name', 'title', 'notes', 'url', 
        'maintainer', 'maintainer_email', 'author', 'author_email', 
        'version', 'url', 'dataset_type'
    ])

    def test_1_create_ckan(self):
        yield self._create, ckan_fixtures['1']

    def test_2_show_ckan(self):
        yield self._show, ckan_fixtures['1']

    def test_3_update_ckan(self):
        yield self._update, ckan_fixtures['1'], '0..1'

    def test_4_create_foo(self):
        # Flat input
        yield self._create, foo_fixtures['1']
        # Nested input 
        yield self._create, foo_fixtures['2']
        # Wrong type
        yield self._create_invalid, foo_fixtures['3'], ['dataset_type']

    def test_5_show_foo(self):
        yield self._show, foo_fixtures['1']

    def test_6_create_and_update_foo(self):
        yield self._create, foo_fixtures['4']
        yield self._update, foo_fixtures['4'], '0..1'

    # Helpers

    @with_request_context('publicamundi-tests', 'index')
    def _create(self, data):
        def_pack = data['0']
        context = { 'model': model, 'session': model.Session, 'ignore_auth': True }
        pkg = toolkit.get_action ('package_create')(context, data_dict=def_pack)
        assert pkg
        assert pkg.get('id')
        assert pkg.get('name')
        self._check_result_for_edit(def_pack, pkg)
        return pkg

    # Exception raised: ValidationError: {'dataset_type': ['Unknown dataset-type (boo)']}
    @nose.tools.raises(Exception)
    @with_request_context('publicamundi-tests', 'index')
    def _create_invalid(self, data, bad_keys):
        def_pack = data['0']
        context = { 'model': model, 'session': model.Session, 'ignore_auth': True }
        pkg = toolkit.get_action ('package_create')(context, data_dict=def_pack)
        #error_dict = pkg.get('error')
        #assert error_dict
        #assert error_dict.get('__type') == 'Validation Error'
        #assert all([ k in error_dict for k in bad_keys ])
        #return pkg

    @with_request_context('publicamundi-tests', 'index')
    def _update(self, data, changeset):
        def_pack = data['0']
        context = { 'model': model, 'session': model.Session, 'ignore_auth':True }
        data[changeset].update({'name':def_pack.get('name')})
        pkg = toolkit.get_action ('package_update')(context, data_dict=data[changeset])
        assert pkg
        assert pkg.get('id')
        assert pkg.get('name')

        # Construct expected dict to check equality with result
        comb_dict = copy.deepcopy(def_pack)
        if changeset != '0':
            for k,v in data[changeset].iteritems():
                comb_dict.update({k: v})
                # Check if updated package equals expected dictionary
            self._check_result_for_edit(comb_dict, pkg)
        else:
            self._check_result_for_edit(data['0'], pkg)

        return pkg

    @with_request_context('publicamundi-tests', 'index')
    def _show(self, data, changeset='0'):
        def_pack = data['0']
        name_or_id = def_pack.get('name')
        context = { 'model': model, 'session': model.Session, 'ignore_auth':True }
        pkg = toolkit.get_action ('package_show') (context, data_dict = {'id': name_or_id})
        assert pkg
        assert pkg.get('id')
        assert pkg.get('name')

        self._check_result_for_edit(data[changeset], pkg)
        return pkg

    def _check_result_for_read(self, data, result):
        pass

    def _check_result_for_edit(self, data, result):
        dt = result.get('dataset_type')
        dt_spec = dataset_types.get(dt)
        assert dt_spec

        dt_prefix = dt_spec.get('key_prefix', dt)
        obj_factory = dt_spec.get('class')

        keys = data.keys()
        core_keys = set(keys) & self.core_keys
        for key in core_keys:
            assert data[key] == result[key]

        # check to avoid case where CKAN doesn't keep old tags on update
        if data.get('tags') and result.get('tags'):
            tags = set(map(lambda t: t['name'] ,data['tags']))
            result_tags = set(map(lambda t: t['name'] ,result['tags']))
            assert tags == result_tags

        dt_keys = filter(lambda t: t.startswith(dt_prefix + '.'), keys)

        # Test only supporting nested fixtures
        if dt_prefix in data:
            expected_obj = obj_factory().from_dict(data[dt_prefix], opts={'unserialize-values': 'default' })
        else:
            expected_obj = obj_factory()

        result_obj = result[dt_prefix]

        print 'expected (fixtures)'
        print expected_obj
        print 'got (api response)'
        print result_obj
        # Test fails here because result_obj is empty
        assert result_obj == expected_obj
        print 'OK'
        return

ckan_fixtures = {
    '1':{
        '0': {
                'name': 'hello-ckan-1',
                'title': u'Hello Ckan 1',
                'tags': [
                    { 'name': 'hello-world', 'display_name': 'Hello World', },
                    { 'name': u'test', 'display_name': 'Test' },
                ],
                'author': u'Foofootos'
            },
        '0..1': {
                'title': u'Hello Ckan 1b',
                'author': u'Foofootos2'
                },
        }
    }
foo_fixtures = {
    '1':{
        '0': {
            'name': 'hello-foo-2-1',
            'title': u'Hello Foo (2.1)',
            'notes': u'I am a _Foo_ dataset!',
            'url': 'http://example.com/datasets/hello-foo-2-1',
            'license_id': 'cc-by',
            'author': u'Baboulas',
            'maintainer': u'Baboulas',
            'author_email': 'baboulas1999@example.com',
            'tags': [
                { 'name': 'hello-world', 'display_name': 'Hello World', }, 
                { 'name': u'test', 'display_name': 'Test' }, 
                { 'name': 'foo', 'display_name': 'Foo' }, 
            ],
            'dataset_type': 'foo',
            'foo':{
                    'baz': u'A second chance',
                    'rating': 2,
                    'grade': 4.75,
                    'reviewed': False,
                    'created': u'2014-02-10T00:00:00',
                    'temporal_extent':{
                                        'start': u'2012-01-01',
                                        'end': u'2013-01-01',
                                        },
                    'thematic_category': 'health',
                    }
            }
        },
    '2':{
        '0': {
                'name': 'hello-foo-2-3',
                'title': u'Hello Foo (2.3)',
                'license_id': 'gfdl',
                'url': 'http://example.com/datasets/hello-foo-2-3',
                'version': '1.0.2',
                'notes': u'I am yet another _Foo_ dataset!',
                'author': u'malex',
                'maintainer': u'Baboulas',
                'author_email': 'malex@example.com',
                'tags': [
                    { 'name': 'hello-world', 'display_name': 'Hello World', }, 
                    { 'name': u'test', 'display_name': 'Test' }, 
                    { 'name': 'foo', 'display_name': 'Foo' }, 
                ],
                'dataset_type': 'foo',
                'foo': {
                    'baz': u'Baobab',
                    'reviewed': False,
                    'rating': 5,
                    'grade': 5.72,
                    'created': u'2014-08-10T00:00:00',
                    'temporal_extent': { 
                        'start': '2012-01-01',
                        'end': '2013-01-01',
                    },
                    'thematic_category': 'health',
                }
            }
        },
    '3':{
        '0': {
            'name': 'helo-boo-3',
            'title': u'Helo Boo 3',
            'dataset_type': 'boo',
        }
    },
    '4':{
        '0':{
                'name': 'hello-foo-4',
                'title': u'Hello Foo (4)',
                'notes': u'I am yet another _Foo_ dataset!',
                'author': u'Nowhere Man',
                'maintainer': u'Nowhere Man',
                'author_email': 'nowhere-man@example.com',
                'tags': [
                    { 'name': 'hello-world', 'display_name': 'Hello World', }, 
                    { 'name': u'test', 'display_name': 'Test' }, 
                    { 'name': 'foo', 'display_name': 'Foo' }, 
                ],
                'dataset_type': 'foo',
                'foo':{
                        'baz': u'Bazzzzz',
                        'rating': 7,
                        }
                },
        '0..1':{
                'title': u'Hello Foo (4)b',
                'dataset_type': 'foo',
                'foo': {
                        'baz': u'Baobab',
                        'rating': 9,
                        'reviewed': False,
                        'grade': 8.2,
                        'created': u'2014-01-10T01:01:02',
                        'temporal_extent':{
                                            'start': '1999-01-01',
                                            'end': '2000-01-01'
                                            },
                        'thematic_category': 'environment',
        }
    }
}
}

