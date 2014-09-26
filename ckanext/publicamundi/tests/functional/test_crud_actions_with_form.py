# -*- encoding: utf-8 -*-

import json
import webtest
import nose.tools
import inflection
import datadiff
import logging
import copy 

from datadiff.tools import assert_equal

from ckan.tests import CreateTestData
from ckan.tests import TestController as BaseTestController

from ckanext.publicamundi.lib import dictization
from ckanext.publicamundi.lib.metadata import dataset_types, Object

log1 = logging.getLogger(__name__)

## Tests ##

class TestController(BaseTestController):

    basic_fields = set([
        'name', 'title', 'notes', 
        'maintainer', 'maintainer_email', 'author', 'author_email', 
        'version', 'url', 'license_id',
    ])
 
    request_headers = {}

    request_environ = {
        'REMOTE_USER': 'tester',
    }

    def __init__(self):
        BaseTestController.__init__(self)
        self.app.extra_environ.update(self.request_environ)
    
    @classmethod
    def setup_class(cls):
        CreateTestData.create_user('tester', about='A tester', password='tester')
        return

    @classmethod
    def teardown_class(cls):
        pass

    def test_1_create_package(self):
        
        yield self._create_package, 'hello-foo-1'
        yield self._create_package_witherr, 'hello-foo-2', 'wrong1'
        
    def test_2_update_package(self):
        
        yield self._update_package, 'hello-foo-1', '0..1'
        yield self._update_package, 'hello-foo-1', '1..2'
        yield self._update_package_witherr, 'hello-foo-2', 'wrong2'
     
    def test_3_create_resource(self):
    
        yield self._create_resource, 'hello-foo-1', 'resource-1'
        yield self._create_resource, 'hello-foo-1', 'resource-2'
     
    def test_4_update_resource(self):
    
        yield self._update_resource, 'hello-foo-1', 'resource-1', '0..1'
        yield self._update_resource, 'hello-foo-1', 'resource-2', '0..1'

    def test_5_delete_resource(self):
    
        yield self._delete_resource, 'hello-foo-1', 'resource-1'
 
    def test_6_delete_package(self):
    
        yield self._delete_package, 'hello-foo-1'

    def _create_package(self, fixture_name):
        
        pkg_dict = package_fixtures[fixture_name]['0'] 
        pkg_name = pkg_dict['name']

        res1 = self.app.get('/dataset/new', status='*')
        assert res1.status == 200
        
        dt = pkg_dict['dataset_type']
        dt_spec = dataset_types[dt]
        key_prefix = dt_spec.get('key_prefix', dt)

        # 1st stage
    
        form1 = res1.forms['package-form'] 

        for k in ['title', 'name', 'dataset_type', 'notes', 'license_id']:
            v = pkg_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form1.set(k, v)
        form1.set('tag_string', ','.join(map(lambda t: t['name'], pkg_dict.get('tags', []))))
        
        res1s = form1.submit('save')
        assert res1s.status in [301, 302] 
        
        # 2nd stage

        res2 = res1s.follow()
        
        resource_dict = next(iter(pkg_dict['resources'])) # 1st resource
        form2 = res2.forms['resource-form']
        for k in ['description', 'url', 'name', 'format']:
            v = resource_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form2.set(k, v)
        
        btns = form2.fields.get('save')
        i2 = next(j for j, b in enumerate(btns) if b.id == 'btn-save-go-metadata')
        res2s = form2.submit('save', index=i2, status='*')
        assert res2s.status in [301, 302]

        # 3rd stage - core metadata

        res3 = res2s.follow()
        
        form3 = res3.forms['package-form']
        for k in ['version', 'url', 'author', 'author_email', 'maintainer', 'maintainer_email']:
            v = pkg_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form3.set(k, v)

        # 3rd stage - dataset_type-related metadata

        for t, v in dictization.flatten(pkg_dict.get(dt)).items():
            k = '.'.join((key_prefix,) + tuple(map(str,t)))
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form3.set(k, v)

        btns = form3.fields.get('save')
        i3 = next(j for j, b in enumerate(btns) if b.id == 'btn-save-finish')
        res3s = form3.submit('save', index=i3, status='*')
        assert res3s.status in [301, 302]

        # Finished, return to "view" page
        
        res4 = res3s.follow()
        assert res4.status in [200]
        assert res4.request.url == '/dataset/%s' %(pkg_name)

        # Compare to package_show result

        res_dict = self._get_package(pkg_name)

        assert res_dict['dataset_type'] == dt

        for k in (self.basic_fields & set(res_dict.keys())):
            assert res_dict[k] == pkg_dict[k]
        pkg_dt_dict = dictization.flatten(pkg_dict.get(dt))
        res_dt_dict = dictization.flatten(res_dict.get(dt))
        for k in pkg_dt_dict.keys():
            assert res_dt_dict[k] == pkg_dt_dict[k]

        return


    def _create_package_witherr(self, fixture_name, changeset):
        
        #pkg_dict = package_fixtures[fixture_name]['0'] 
        pkg_dict = package_fixtures[fixture_name]['0'] 
        wrng_pkg_dict = package_fixtures[fixture_name][changeset] 
        pkg_name = pkg_dict['name']

        res1 = self.app.get('/dataset/new', status='*')
        assert res1.status == 200
        
        dt = pkg_dict['dataset_type']
        dt_spec = dataset_types[dt]
        key_prefix = dt_spec.get('key_prefix', dt)

        # 1st stage
    
        form1 = res1.forms['package-form'] 

        for k in ['title', 'name', 'dataset_type', 'notes', 'license_id']:
            v = pkg_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form1.set(k, v)
        form1.set('tag_string', ','.join(map(lambda t: t['name'], pkg_dict.get('tags', []))))
        
        res1s = form1.submit('save')
        assert res1s.status in [301, 302] 
        
        # 2nd stage

        res2 = res1s.follow()
        
        resource_dict = next(iter(pkg_dict['resources'])) # 1st resource
        form2 = res2.forms['resource-form']
        for k in ['description', 'url', 'name', 'format']:
            v = resource_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form2.set(k, v)
        
        btns = form2.fields.get('save')
        i2 = next(j for j, b in enumerate(btns) if b.id == 'btn-save-go-metadata')
        res2s = form2.submit('save', index=i2, status='*')
        assert res2s.status in [301, 302]

        # 3rd stage - core metadata

        res3 = res2s.follow()
        
        form3 = res3.forms['package-form']
        for k in ['version', 'url', 'author', 'author_email', 'maintainer', 'maintainer_email']:
            v = wrng_pkg_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form3.set(k, v)

        # 3rd stage - dataset_type-related metadata

        for t, v in dictization.flatten(wrng_pkg_dict.get(dt)).items():

            k = '.'.join((key_prefix,) + tuple(map(str,t)))
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form3.set(k, v)

        btns = form3.fields.get('save')
        i3 = next(j for j, b in enumerate(btns) if b.id == 'btn-save-finish')
        res3s = form3.submit('save', index=i3, status='*')
        #assert res3s.status in [301, 302]
       
       # validation error leads to code 200 instead of redirect
        #assert res3s.status in [200]
        assert res3s.status in [200]
        
        form4 = res3s.forms['package-form']
        
        #readd already previous correct fields
        # TODO bug?
        for k in ['version', 'url', 'author', 'author_email', 'maintainer', 'maintainer_email']:
            if k in wrng_pkg_dict:
                v = wrng_pkg_dict.get(k)
            else:
                v = pkg_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form4.set(k, v)

        for t, v in dictization.flatten(wrng_pkg_dict.get(dt)).items():
            k = '.'.join((key_prefix,) + tuple(map(str,t)))
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form4.set(k, v)

        for t, v in dictization.flatten(pkg_dict.get(dt)).items():
            k = '.'.join((key_prefix,) + tuple(map(str,t)))
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form4.set(k, v)

        # make sure form is built with all foo elements
        for fld in form4.fields.keys():
            if fld.startswith('foo'):
                key = fld.split('.')[1]
                assert key in pkg_dict.get(dt)
        
        #form4.set('foo.baz', u'BaoAb')

        # fill in the correct value
        #form4.set('foo.'+field, correct_val)
        
        # update dict
        #pkg_dict['foo'][field] = correct_val
        #print form3

        res3s = form4.submit('save', index=i3, status='*')
        assert res3s.status in [301, 302]

        # Finished, return to "view" page
        
        res4 = res3s.follow()
        assert res4.status in [200]
        assert res4.request.url == '/dataset/%s' %(pkg_name)

        # Compare to package_show result

        res_dict = self._get_package(pkg_name)

        assert res_dict['dataset_type'] == dt
        for k in (self.basic_fields & set(res_dict.keys())):
            if k in pkg_dict:
                print res_dict[k]
                print pkg_dict[k]
                assert res_dict[k] == pkg_dict[k]
            else:
                print res_dict[k]
                print wrng_pkg_dict[k]
                assert res_dict[k] == wrng_pkg_dict[k]

        pkg_dt_dict = dictization.flatten(pkg_dict.get(dt))
        wrng_pkg_dt_dict = dictization.flatten(wrng_pkg_dict.get(dt))
        res_dt_dict = dictization.flatten(res_dict.get(dt))
        for k in pkg_dt_dict.keys():
            if k in pkg_dt_dict:
                assert res_dt_dict[k] == pkg_dt_dict[k]
            else:
                assert res_dt_dict[k] == wrng_pkg_dt_dict[k]

        return

    def _update_package(self, fixture_name, changeset):
 
        assert fixture_name in package_fixtures
        pkg_dict = package_fixtures[fixture_name][changeset]
        pkg_name = package_fixtures[fixture_name]['0']['name']
        
        res1 = self.app.get('/dataset/edit/%s' % pkg_name)
        assert res1.status == 200
        
        dt = package_fixtures[fixture_name]['0']['dataset_type']
        dt_spec = dataset_types[dt]
        key_prefix = dt_spec.get('key_prefix', dt)

        # Edit core metadata
        
        form1 = res1.forms['package-form']
        for k in self.basic_fields :
            v = pkg_dict.get(k)
            if v is not None:
                v = v.encode('utf-8') if isinstance(v, unicode) else v
                form1.set(k, v)
        if 'tags' in pkg_dict:
            form1.set('tag_string', ','.join(map(lambda t: t['name'], pkg_dict.get('tags', []))))
        
        # Edit dataset_type-related metadata

        for t, v in dictization.flatten(pkg_dict.get(dt)).items():
            k = '.'.join((key_prefix,) + t)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form1.set(k, v)
        
        # Submit

        res1s = form1.submit('save', status='*')
        assert res1s.status in [301, 302]
        
        res2 = res1s.follow()
        assert res2.status in [200]      
        assert res2.request.url == '/dataset/%s' %(pkg_name)

    def _update_package_witherr(self, fixture_name, changeset):
 
        assert fixture_name in package_fixtures
        pkg_dict = package_fixtures[fixture_name]['0']
        wrng_pkg_dict = package_fixtures[fixture_name][changeset]
        
        pkg_name = package_fixtures[fixture_name]['0']['name']
        
        res1 = self.app.get('/dataset/edit/%s' % pkg_name)
        assert res1.status == 200
        
        dt = package_fixtures[fixture_name]['0']['dataset_type']
        dt_spec = dataset_types[dt]
        key_prefix = dt_spec.get('key_prefix', dt)

        # Edit core metadata
        
        form1 = res1.forms['package-form']
        for k in self.basic_fields :
            v = wrng_pkg_dict.get(k)
            if v is not None:
                v = v.encode('utf-8') if isinstance(v, unicode) else v
                form1.set(k, v)
        if 'tags' in pkg_dict:
            form1.set('tag_string', ','.join(map(lambda t: t['name'], wrng_pkg_dict.get('tags', []))))
        
        # Edit dataset_type-related metadata

        for t, v in dictization.flatten(wrng_pkg_dict.get(dt)).items():
            k = '.'.join((key_prefix,) + t)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form1.set(k, v)
            print k
            print v
        
        # Submit

        res1s = form1.submit('save', status='*')
        #assert res1s.status in [301, 302]

        # validation error leads to code 200 instead of redirect
        assert res1s.status in [200]
        form2 = res1.forms['package-form']
        for k in self.basic_fields :
            v = pkg_dict.get(k)
            if v is not None:
                v = v.encode('utf-8') if isinstance(v, unicode) else v
                form2.set(k, v)
        if 'tags' in pkg_dict:
            form2.set('tag_string', ','.join(map(lambda t: t['name'], pkg_dict.get('tags', []))))
        
        # Edit dataset_type-related metadata

        for t, v in dictization.flatten(pkg_dict.get(dt)).items():
            k = '.'.join((key_prefix,) + t)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form2.set(k, v)

        # make sure form is built with all foo elements
        for fld in form2.fields.keys():
            if fld.startswith('foo'):
                key = fld.split('.')[1]
                assert key in pkg_dict.get(dt)
        
        # fill in the correct value
        #form2.set('foo.'+field, correct_val)
        
        # update dict
        #pkg_dict['foo'][field] = correct_val

# Submit

        res1s = form1.submit('save', status='*')
        assert res1s.status in [301, 302]
        
        res2 = res1s.follow()
        assert res2.status in [200]      
        assert res2.request.url == '/dataset/%s' %(pkg_name)


    def _delete_package(self, fixture_name):
 
        assert fixture_name in package_fixtures
        pkg_dict = package_fixtures[fixture_name]
        pkg_name = package_fixtures[fixture_name]['0']['name']
        
        res_pkg_dict = self._get_package(pkg_name)
        res1 = self.app.get('/dataset/delete/%s' % pkg_name)
        assert res1.status == 200

        dt = package_fixtures[fixture_name]['0']['dataset_type']
        dt_spec = dataset_types[dt]
        key_prefix = dt_spec.get('key_prefix', dt)

        form1 = res1.forms[1]
        
        # Confirm
        res1s = form1.submit('delete', status='*')
        assert res1s.status in [301, 302]

        res2 = res1s.follow()
        assert res2.status in [200]
        assert res2.request.url == '/dataset'

        res = self.app.get('/api/action/package_list')
        assert res.json.get('success')
        assert pkg_name not in res.json.get('result')

    def _create_resource(self, pkg_fixture_name, fixture_name):
        
        assert pkg_fixture_name in package_fixtures
        assert fixture_name in resource_fixtures
        pkg_name = package_fixtures[pkg_fixture_name]['0']['name']
        resource_dict = resource_fixtures[fixture_name]['0']
        resource_name = resource_dict['name']
        
        # Fetch initial package dict
        
        pkg_dict = self._get_package(pkg_name)
        
        dt = pkg_dict['dataset_type']

        # Create resource

        res1 = self.app.get('/dataset/new_resource/%s' % pkg_name)
        assert res1.status == 200

        form1 = res1.forms['resource-form']
        for k in ['description', 'url', 'name', 'format']:
            v = resource_dict.get(k)
            v = v.encode('utf-8') if isinstance(v, unicode) else v
            form1.set(k, v)
        
        res1s = form1.submit('save', status='*')
        assert res1s.status in [301, 302]
        
        res2 = res1s.follow()
        assert res2.status in [200]      
        assert res2.request.url == '/dataset/%s' %(pkg_name)

        # Fetch result package dict
        
        res_pkg_dict = self._get_package(pkg_name)
        res_pkg_resources = res_pkg_dict['resources']

        # Verify resource metadata (changed)

        res_resource_dict = next(r for r in res_pkg_resources if r['name'] == resource_name)
        for k in ['url', 'description', 'name']:
            assert resource_dict[k] == res_resource_dict[k]
        assert resource_dict['format'] == res_resource_dict['format'].lower()

        # Verify package metadata (not changed)

        for k in self.basic_fields:
            assert pkg_dict[k] == res_pkg_dict[k] 
        
        assert_equal(pkg_dict.get(dt), res_pkg_dict.get(dt))

    def _update_resource(self, pkg_fixture_name, fixture_name, changeset):
        
        assert pkg_fixture_name in package_fixtures
        assert fixture_name in resource_fixtures
        pkg_name = package_fixtures[pkg_fixture_name]['0']['name']
        resource_name = resource_fixtures[fixture_name]['0']['name']
        resource_dict = resource_fixtures[fixture_name][changeset]
        
        # Fetch initial package dict
        
        pkg_dict = self._get_package(pkg_name)
        
        pkg_resources = pkg_dict['resources']
        dt = pkg_dict['dataset_type']
        
        resource_id = next(r for r in pkg_resources if r['name'] == resource_name).get('id')
        
        # Update resource
        
        res1 = self.app.get('/dataset/%s/resource_edit/%s' % (pkg_name, resource_id))
        assert res1.status == 200
        
        form1 = res1.forms['resource-form']
        for k in ['description', 'url', 'name', 'format']:
            v = resource_dict.get(k)
            if v is not None:
                v = v.encode('utf-8') if isinstance(v, unicode) else v
                form1.set(k, v)
        
        res1s = form1.submit('save', status='*')
        assert res1s.status in [301, 302]
        
        res2 = res1s.follow()
        assert res2.status in [200]      
        assert res2.request.url == '/dataset/%s/resource/%s' %(pkg_name, resource_id)

        # Fetch result package dict
       
        res_pkg_dict = self._get_package(pkg_name)
        res_pkg_resources = res_pkg_dict['resources']
        
        # Verify resource metadata (changed)
        
        resource_name = resource_dict.get('name', resource_name)
        res_resource_dict = next(r for r in res_pkg_resources if r['name'] == resource_name)
        for k in ['url', 'description', 'name']:
            assert not(k in resource_dict) or (resource_dict[k] == res_resource_dict[k])
        if 'format' in resource_dict:
            assert resource_dict['format'] == res_resource_dict['format'].lower()
    
        # Verify package metadata (not changed)

        for k in self.basic_fields:
            assert pkg_dict[k] == res_pkg_dict[k] 
        
        assert_equal(pkg_dict.get(dt), res_pkg_dict.get(dt))

    def _delete_resource(self, pkg_fixture_name, fixture_name):
        
        assert pkg_fixture_name in package_fixtures
        assert fixture_name in resource_fixtures

        pkg_name = package_fixtures[pkg_fixture_name]['0']['name']
        resource_name = resource_fixtures[fixture_name]['0']['name']
        resource_dict = resource_fixtures[fixture_name]
        
        # Fetch initial package dict
        
        pkg_dict = self._get_package(pkg_name)
        
        pkg_resources = pkg_dict['resources']
        dt = pkg_dict['dataset_type']

        resource_id = next(r for r in pkg_resources if r['name'] == resource_name).get('id')
        
        # Delete resource
        
        res1 = self.app.get('/dataset/%s/resource_delete/%s' % (pkg_name, resource_id))
        assert res1.status == 200

        # Note forms[1] is the delete confirmation form
        form1 = res1.forms[1]

        res1s = form1.submit('delete', status='*')
        assert res1s.status in [301, 302]

        res12 = self.app.get('/dataset/%s/resource_delete/%s' % (pkg_name, resource_id))
        assert res12.status == 200

        res2 = res1s.follow()
        assert res2.status in [200]
        assert res2.request.url == '/dataset/%s' %(pkg_name)

        # Fetch result package dict
       
        res_pkg_dict = self._get_package(pkg_name)
        res_pkg_resources = res_pkg_dict['resources']

        # Verify resource metadata deleted

        for res in res_pkg_resources:
            assert res.get('name') != resource_name
            

        # Verify package metadata (not changed)

        for k in self.basic_fields:
            assert pkg_dict[k] == res_pkg_dict[k] 
        
        assert_equal(pkg_dict.get(dt), res_pkg_dict.get(dt))
    def _get_package(self, pkg_name):
        
        res = self.app.get('/api/action/package_show?id=%s' %(pkg_name))
        assert res.json.get('success')
        return res.json.get('result')

## Fixtures ##

resource_fixtures = {}

resource_fixtures['resource-1'] = {
    '0': {
        'url': 'http://example.com/res/1',
        'name': u'Example 1',
        'format': 'html',
        'description': u'A very important HTML document',
    },
    '0..1': {
        'name': u'Example webpage (1)',
        'description': u'A quite important HTML document',
    }
}

resource_fixtures['resource-2'] = {
    '0': {
        'url': 'http://localhost:5001/samples/1.csv',
        'name': u'Example 2',
        'format': 'csv',
        'description': u'A sample CSV file',
    },
    '0..1': {
        'name': 'Example CSV (2)',
    },
}

resource_fixtures['resource-3'] = {
    '0': {
        'url': 'http://localhost:5001/api/action',
        'name': u'Example API',
        'format': 'api',
        'description': u'An example API endpoint',
    },
}

package_fixtures = {}
package_fixtures['hello-foo-1'] = {
    '0': {
        'title': u'Hello Foo (1)',
        'name': 'hello-foo-1',
        'notes': u'I am the first _Foo_ dataset!',
        'author': u'Λαλάκης',
        'license_id': 'gfdl',
        'version': '1.0.0',
        'maintainer': u'Nowhere Man',
        'author_email': 'lalakis.1999@example.com',
        'maintainer_email': 'nowhere-man@example.com',
        'url': 'http://example.com/datasets/hello-foo-1',
        'tags': [ 
            { 'name': 'hello-world', 'display_name': 'Hello World', }, 
            { 'name': u'test', 'display_name': 'Test' }, 
            { 'name': 'foo', 'display_name': 'Foo' }, 
        ],
        'dataset_type': 'foo',
        'foo': {
            'baz': u'BaoBab Tree',
            'rating': 9,
            'grade': 5.12,
            'reviewed': False,
            'created': u'2014-09-13T17:00:00',
            'temporal_extent': { 
                'start': '2012-01-01',
                'end': '2013-01-01',
            },
            'thematic_category': 'health',
        },
        'resources': [
            resource_fixtures['resource-1']['0'],
        ],
    },
    '0..1': {
        'license_id': 'cc-by',
        'version': '1.0.1',
        'foo': {
            'baz': u'Ενα δενδρο BaoBab',
            'grade': 6.89,
            'reviewed': True,
            'thematic_category': 'environment',
        },
    },
    '1..2': {
        'version': '1.0.2',
        'foo': {
            'rating': 7,
            'temporal_extent': {
                'start': '2012-09-01',
                'end': '2013-09-01',
            }, 
        }, 
    },
}

package_fixtures['hello-foo-2'] = {
    '0': {
        'title': u'Hello Foo (2)',
        'name': 'hello-foo-2',
        'notes': u'I am the second _Foo_ dataset!',
        'author': u'Λαλάκης',
        'license_id': 'gfdl',
        'version': '1.0.0',
        'maintainer': u'Nowhere Man',
        'author_email': 'lalakis.1999@example.com',
        'maintainer_email': 'nowhere-man@example.com',
        'url': 'http://example.com/datasets/hello-foo-2',
        'tags': [ 
            { 'name': 'hello-world', 'display_name': 'Hello World', }, 
            { 'name': u'test', 'display_name': 'Test' }, 
            { 'name': 'foo', 'display_name': 'Foo' }, 
        ],
        'dataset_type': 'foo',
        'foo': {
            'baz': u'bzzzz',
            'rating': 9,
            'grade': 5.12,
            'reviewed': False,
            'created': u'2014-09-13T17:00:00',
            'temporal_extent': {
                'start': '2012-01-01',
                'end': '2013-01-01',
            },
            'thematic_category': 'health',
        },
        'resources': [
            resource_fixtures['resource-1']['0'],
        ],
    },
    '': {
        'foo': {
            'baz': u'Ενα δενδρο BaoBab',
            'grade': 6.89,
            'reviewed': True,
            'thematic_category': 'environment',
        },
    },
    'wrong1': {
        'foo': {
            'baz': u'B',
            'grade': 6.89,
            'reviewed': True,
            'thematic_category': 'environment',
        },
    },
    'wrong2': {
        'foo': {
            'baz': u'B',
            'grade': 26.89,
            'reviewed': True,
            'thematic_category': 'environment',
        },
    },

}

