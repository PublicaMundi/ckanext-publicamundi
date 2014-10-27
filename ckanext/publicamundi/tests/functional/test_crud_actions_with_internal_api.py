# -*- encoding: utf-8 -*-

import nose.tools
import json
import collections
import copy
import ckan.tests
import pprint

import ckan.model as model
import ckan.plugins.toolkit as toolkit

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib import dictization
from ckanext.publicamundi.lib.metadata import types
from ckanext.publicamundi.lib.metadata import dataset_types, Object
from ckanext.publicamundi.tests.functional import with_request_context
from ckanext.publicamundi.tests import fixtures
class TestController(ckan.tests.TestController):
    
    core_keys = set([
        'name', 'title', 'notes', 'url', 
        'maintainer', 'maintainer_email', 'author', 'author_email', 
        'version', 'url', 'dataset_type'
    ])

    @classmethod
    def get_action_context(cls):
        return {
            'model': model, 
            'session': model.Session, 
            'user': 'tester',
            'ignore_auth':True, 
            'api_version': 3,
        }
    
    @nose.tools.istest
    def test_1_create(self):
       
        yield self._create, 'ckan', 'hello-ckan-i-1'
        yield self._create, 'ckan', 'hello-ckan-i-2'
        yield self._create, 'foo', 'hello-foo-i-1' 
        yield self._create, 'foo', 'hello-foo-i-2' 
        yield self._create, 'foo', 'hello-foo-i-3' 
        #yield self._create, 'inspire', 'inspire-1'
        yield self._create_invalid, 'foo', 'hello-boo', set(['dataset_type'])
        yield self._create_invalid, 'foo', 'hello-foo-i-4', set(['foo.baz', 'foo.rating'])
        pass

    @nose.tools.istest
    def test_2_show(self):
        
        yield self._show, 'ckan', 'hello-ckan-i-1'
        yield self._show, 'ckan', 'hello-ckan-i-2'
        yield self._show, 'foo', 'hello-foo-i-1'
        pass

    @nose.tools.istest
    def test_3_update(self):
        
        yield self._update, 'ckan', 'hello-ckan-i-1', '0a'
        yield self._update, 'foo', 'hello-foo-i-3', '0a'
        pass

    # Helpers

    @with_request_context('publicamundi-tests', 'index')
    def _create(self, dt, name):
        global pkg_fixtures
        
        context = self.get_action_context()
        pkg_dict = pkg_fixtures[dt][name]['0']
        pkg = toolkit.get_action('package_create')(context, data_dict=pkg_dict)

        assert pkg and pkg.get('id') and pkg.get('name')
        self._check_result_for_edit(pkg_dict, pkg)
        pass
    
    @with_request_context('publicamundi-tests', 'index')
    def _show(self, dt, name):
        global pkg_fixtures
        
        context = self.get_action_context()
        pkg_dict = pkg_fixtures[dt][name]['0']
        name_or_id = pkg_dict.get('name')
        data_dict = { 'id': name_or_id }
        pkg = toolkit.get_action('package_show')(context, data_dict=data_dict)
        
        assert pkg and pkg.get('id') and pkg.get('name')
        pass
    
    @with_request_context('publicamundi-tests', 'index')
    def _update(self, dt, name, changeset):
        global pkg_fixtures
        
        context = self.get_action_context()
        pkg_dict = pkg_fixtures[dt][name]['0']
        pkg_dict = dictization.update_deep(
            copy.deepcopy(pkg_dict), pkg_fixtures[dt][name][changeset])
        
        pkg = toolkit.get_action('package_update')(context, data_dict=pkg_dict)
        
        assert pkg and pkg.get('id') and pkg.get('name')
        self._check_result_for_edit(pkg_dict, pkg)
        pass

    @with_request_context('publicamundi-tests', 'index')
    def _create_invalid(self, dt, name, bad_keys):
        
        context = self.get_action_context()
        pkg_dict = pkg_fixtures[dt][name]['0']
        
        try:
            pkg = toolkit.get_action('package_create')(context, data_dict=pkg_dict)
        except toolkit.ValidationError as ex:
            assert bad_keys.issubset(ex.error_dict.keys())
        else:
            assert False, 'This should have failed!'

        pass

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

        if data.get('tags') and result.get('tags'):
            tags = set(map(lambda t: t['name'], data['tags']))
            result_tags = set(map(lambda t: t['name'], result['tags']))
            assert tags == result_tags

        dt_keys = filter(lambda t: t.startswith(dt_prefix + '.'), keys)
        
        # Note The input data may be in either flat or nested format

        expected_obj = obj_factory()
        if dt_prefix in data:
            # Load from nested input data
            expected_obj.from_dict(
                data[dt_prefix], is_flat=0, 
                opts={'unserialize-values': 'default'})
        else:
            # Load from flattened input data
            expected_obj.from_dict(
                data, is_flat=1, 
                opts={
                    'unserialize-keys': True,
                    'key-prefix': dt_prefix,
                    'unserialize-values': 'default'
                })
            
        result_obj = result[dt_prefix]
        assert result_obj == expected_obj
        pass

#
# Fixtures
#

ckan_fixtures = {
    'hello-ckan-i-1': {
        '0': {
            'name': 'hello-ckan-i-1',
            'title': u'Hello Ckan (i1)',
            'tags': [
                {'name': 'hello-world', 'display_name': 'Hello World', },
                {'name': u'test', 'display_name': 'Test'},
            ],
            'author': u'Foofootos'
        },
        '0a': {
            'title': u'Hello Ckan (i1-a)',
            'author': u'Foofootos2'
        },
    },
    'hello-ckan-i-2': {
        '0': {
            'name': 'hello-ckan-i-2',
            'title': u'Hello Ckan (i2)',
            'tags': [
                {'name': 'hello-world', 'display_name': 'Hello World', },
                {'name': u'test', 'display_name': 'Test'},
            ],
            'author': u'Τοτος'
        },
    },
}

foo_fixtures = {
    'hello-foo-i-1': {
        '0': {
            'name': 'hello-foo-i-1',
            'title': u'Hello Foo (i1)',
            'notes': u'I am a _Foo_ dataset!',
            'url': 'http://example.com/datasets/hello-foo-i-1',
            'license_id': 'cc-by',
            'author': u'Baboulas',
            'maintainer': u'Baboulas',
            'author_email': 'baboulas1999@example.com',
            'tags': [
                {'name': 'hello-world', 'display_name': 'Hello World', },
                {'name': u'test', 'display_name': 'Test'},
                {'name': 'foo', 'display_name': 'Foo'},
            ],
            'dataset_type': 'foo',
            'foo': {
                'baz': u'Μπαζζζζζ',
                'rating': -2,
                'grade': 4.79,
                'reviewed': False,
                'created': u'2014-02-10T00:00:00',
                'temporal_extent': {
                    'start': u'2012-02-01',
                    'end': u'2013-02-01',
                },
                'thematic_category': 'health',
            }
        }
    },
    'hello-foo-i-2': {
        '0': {
            'name': 'hello-foo-i-2',
            'title': u'Hello Foo (i2)',
            'license_id': 'gfdl',
            'url': 'http://example.com/datasets/hello-foo-i-2',
            'version': '1.0.2',
            'notes': u'I am yet another _Foo_ dataset!',
            'author': u'malex',
            'maintainer': u'Baboulas',
            'author_email': 'malex@example.com',
            'tags': [
                {'name': 'hello-world', 'display_name': 'Hello World', },
                {'name': u'test', 'display_name': 'Test'},
                {'name': 'foo', 'display_name': 'Foo'},
            ],
            'dataset_type': 'foo',
            'foo.baz': u'Another Baz',
            'foo.rating': 8,
            'foo.grade': 4.75,
            'foo.reviewed': True,
            'foo.created': u'2014-08-10T21:00:00',
            'foo.temporal_extent.start': '2012-01-01',
            'foo.temporal_extent.end': '2013-01-01',
            'foo.thematic_category': 'environment',
        }
    },
    'hello-boo': {
        '0': {
            'name': 'helo-boo-3',
            'title': u'Helo Boo 3',
            'dataset_type': 'boo',
        }
    },
    'hello-foo-i-3': {
        '0': {
            'name': 'hello-foo-i-3',
            'title': u'Hello Foo (i3)',
            'notes': u'I am yet another _Foo_ dataset!',
            'author': u'Nowhere Man',
            'maintainer': u'Nowhere Man',
            'author_email': 'nowhere-man@example.com',
            'tags': [
                {'name': 'hello-world', 'display_name': 'Hello World', },
                {'name': u'test', 'display_name': 'Test'},
                {'name': 'foo', 'display_name': 'Foo'},
            ],
            'dataset_type': 'foo',
            'foo': {
                'baz': u'Bazzzzz',
                'rating': 7,
            }
        },
        '0a': {
            'title': u'Hello Foo (i3-a)',
            'dataset_type': 'foo',
            'foo': {
                'baz': u'A baobab tree',
                'rating': 9,
                'reviewed': False,
                'grade': 8.2,
                'created': u'2014-01-10T01:01:02',
                'temporal_extent': {
                    'start': '1997-01-01',
                    'end': '1998-01-01'
                },
                'thematic_category': 'environment',
            }
        }
    },
    'hello-foo-i-4': {
        '0': {
            'name': 'hello-foo-i-4',
            'title': u'Hello Foo (i-4)',
            'notes': u'I will never get created because i am bad!',
            'author': u'Nowhere Man',
            'maintainer': u'Nowhere Man',
            'author_email': 'nowhere-man@example.com',
            'tags': [
                {'name': 'hello-world', 'display_name': 'Hello World', },
            ],
            'dataset_type': 'foo',
            'foo': {
                'baz': u'B', # too short
                'rating': 100, # out of range
                'grade': 8.2,
                'thematic_category': 'health',
                'notes': u'Blah Blah',
                'wakeup_time': '08:35:00',
            },
        },
    },
}

#inspire_fixtures = {
#        'inspire-1':{
#            '0':{
#                'title': u'Inspire-test-1',
#                'name': 'inspire-test-1',
#                'dataset_type': 'inspire',
#                'inspire': fixtures.inspire1
#                }
#            }
#        }
pkg_fixtures = {
    'foo': foo_fixtures,
    'ckan': ckan_fixtures,
#    'inspire': inspire_fixtures
}

