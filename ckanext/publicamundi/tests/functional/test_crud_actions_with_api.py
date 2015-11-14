# -*- encoding: utf-8 -*-

import nose.tools
import json
import collections
import copy

import ckan.tests

from ckanext.publicamundi.lib.metadata import factory_for_metadata

class TestController(ckan.tests.TestController):
    
    core_keys = set([
        'name', 'title', 'notes', 'url', 
        'maintainer', 'maintainer_email', 'author', 'author_email', 
        'version', 'url',
    ])
    
    request_headers = {
        'Content-Type': 'application/json',
    }

    request_environ = {
        'REMOTE_USER': 'tester',
    }

    @nose.tools.istest
    def test_1_create_ckan(self):
        
        data = {
            'name': 'helo-ckan-1',
            'title': u'Helo Ckan 1',
            'tags': [
                { 'name': 'hello-world', 'display_name': 'Hello World', }, 
                { 'name': u'test', 'display_name': 'Test' }, 
            ],
        }
        
        result = self._create(data)

    @nose.tools.istest
    def test_2_create_foo(self):

        # Create with flat input 

        data1 = {
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
            'foo.description': u'A great foo dataset',
            'foo.baz': u'A second chance',
            'foo.rating': 2,
            'foo.grade': 4.75,
            'foo.reviewed': False,
            'foo.created': u'2014-08-10T00:00:00',
            'foo.temporal_extent.start': '2012-01-01',
            'foo.temporal_extent.end': '2013-01-01',
            'foo.thematic_category': 'health',
        }
        result1 = self._create(data1)
        result1 = self._show(result1.get('name'))
        
        # Create with flat input (non-ascii strings)
        data2 = copy.deepcopy(data1)
        data2.update({
            'name': 'hello-foo-2-2',
            'title': u'Hello Foo (2.2)',
            'url': 'http://example.com/datasets/hello-foo-2-2',
            'notes': u'I am another  _Foo_ dataset!',
            'foo.baz': u'Ταρατατζουμ',
        })
        result2 = self._create(data2)
        result2 = self._show(result2.get('name'))
    
        # Create with nested input

        data3 = {
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
                'description': u'Ακομη ενα foo σύνολο δεδομένων!',
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
        result3 = self._create(data3)
        result3 = self._show(result3.get('name'))
    
    @nose.tools.istest
    def test_3_create_invalid_type(self):
        data = {
            'name': 'helo-boo-3',
            'title': u'Helo Boo 3',
            'dataset_type': 'boo',
        }
        # This should fail (no such dataset-type)
        result = self._create_invalid(data, bad_keys=['dataset_type'])
    
    @nose.tools.istest
    def test_4_create_and_update_foo(self):
         
        data = {
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
            'foo.baz': u'Bazzzzz',
            'foo.rating': 7,
        } 
        result = self._create(data)

        data.update({            
            'foo.baz': u'Baobab',
            'foo.rating': 9,
            'foo.reviewed': False,
            'foo.grade': 8.2,
            'foo.created': u'2014-08-10T00:00:00',
            'foo.temporal_extent.start': '1999-01-01',
            'foo.temporal_extent.end': '2000-01-01',
            'foo.thematic_category': 'environment',
        })
        result = self._update(data)
    
    def _create_invalid(self, data, bad_keys):
        response = self.app.post('/api/action/package_create', json.dumps(data), 
            headers=self.request_headers, extra_environ=self.request_environ, status='*')
    
        assert response 
        assert response.status >= 400 and response.status < 500
        assert response.json and not response.json.get('success') 

        error_dict = response.json.get('error')
        assert error_dict
        assert error_dict.get('__type') == 'Validation Error'
        assert all([ k in error_dict for k in bad_keys ])
    
    # Helpers

    def _create(self, data):
        response = self.app.post('/api/action/package_create', json.dumps(data), 
            headers=self.request_headers, extra_environ=self.request_environ, status='*')
            
        assert response and response.status in [200, 201]
        assert response.json and response.json.get('success') 
        
        result = response.json.get('result')
        assert result.get('id')
        assert result.get('name')
        
        self._check_result_for_edit(data, result)

        print json.dumps(result, indent=4)
        return result
     
    def _update(self, data):
        response = self.app.post('/api/action/package_update', json.dumps(data), 
            headers=self.request_headers, extra_environ=self.request_environ, status='*')
            
        assert response and response.status in [200, 201]
        assert response.json and response.json.get('success') 
        
        result = response.json.get('result')
        assert result.get('id')
        assert result.get('name')
        
        self._check_result_for_edit(data, result)

        print json.dumps(result, indent=4)
        return result
    
    def _show(self, name_or_id):
        data = { 'id': name_or_id }
        response = self.app.post('/api/action/package_show', json.dumps(data), 
            headers=self.request_headers, extra_environ=self.request_environ, status='*')
        
        assert response and response.status == 200
        assert response.json and response.json.get('success') 
        
        result = response.json.get('result')
        assert result.get('id')
        assert result.get('name')
 
        print json.dumps(result, indent=4)
        return result

    def _check_result_for_read(self, data, result):
        pass
    
    def _check_result_for_edit(self, data, result):
        
        key_prefix = dtype = result.get('dataset_type')
        obj_factory = factory_for_metadata(dtype)

        keys = data.keys()

        core_keys = set(keys) & self.core_keys
        for key in core_keys:
            assert data[key] == result[key]
        
        tags = set(map(lambda t: t['name'] ,data['tags']))
        result_tags = set(map(lambda t: t['name'] ,result['tags']))
        assert tags == result_tags

        result_dict = result.get(key_prefix, {})
        result_obj = obj_factory().from_dict(result_dict, is_flat=False, opts={ 
            'unserialize-values': 'json-s' 
        })
        result_flattened_dict = result_obj.to_dict(flat=True, opts={
            'serialize-keys': True, 
            'serialize-values': 'json-s', 
            'key-prefix': key_prefix 
        })
        dt_keys = filter(lambda t: t.startswith(key_prefix + '.'), keys)
        missing_keys = set(dt_keys) - set(result_flattened_dict.keys())
        assert not missing_keys
        for k in dt_keys:
            assert result_flattened_dict[k] == data[k]

        return

