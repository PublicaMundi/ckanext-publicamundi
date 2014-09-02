import nose.tools
import json
import collections

import ckan.tests

class TestController(ckan.tests.TestController):
    
    @nose.tools.istest
    def test_create_valid_1(self):
        
        data = {
            'name': 'helo-ckan-1',
            'title': u'Helo Ckan 1',
            'tags': [
                { 'name': u'hello-world' }, 
                { 'name': u'test' }, ],
        }
        result = self._test_create(data)

    @nose.tools.istest
    def test_create_valid_2(self):
        data = {
            'name': 'helo-foo-1',
            'title': u'Helo Foo 1',
            'dataset_type': 'foo',
        }
        result = self._test_create(data)
     
    @nose.tools.istest
    def test_create_invalid_1(self):
        data = {
            'name': 'helo-boo-1',
            'title': u'Helo Boo 1',
            'dataset_type': 'boo',
        }
        # This should fail (no such dataset-type)
        result = self._test_create_invalid(data, bad_keys=['dataset_type'])
   
    def _test_create_invalid(self, data, bad_keys):
        response = self.app.post('/api/action/package_create', json.dumps(data), 
            headers = {
                'Content-Type': 'application/json',
            }, 
            extra_environ = {
                'REMOTE_USER': 'tester',
            },
            status = '*')
    
        assert response
        assert response.status >= 400 and response.status < 500
        assert response.json
        assert not response.json.get('success') 

        error_dict = response.json.get('error')
        assert error_dict
        assert error_dict.get('__type') == 'Validation Error'
        assert all([ k in error_dict for k in bad_keys ])
 
    def _test_create(self, data):
        response = self.app.post('/api/action/package_create', json.dumps(data), 
            headers = {
                'Content-Type': 'application/json',
            }, 
            extra_environ = {
                'REMOTE_USER': 'tester',
            },
            status = '*')
    
        assert response    
        assert response.status in [200, 201]
        assert response.json
        assert response.json.get('success') 
        
        result = response.json.get('result')
        assert result.get('id')
        assert result.get('name') == data.get('name')
        assert result.get('title') == data.get('title')
        
        return result

