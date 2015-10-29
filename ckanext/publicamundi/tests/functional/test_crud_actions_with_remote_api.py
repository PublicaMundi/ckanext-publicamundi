import os
import json
import ckanapi
import nose.tools
from ConfigParser import ConfigParser

from ckan.logic import ValidationError

config_file = os.environ.get('CKAN_TEST_CONFIG', 'test-core.ini')
assert os.path.exists(config_file), 'The path for a test-*.ini file is needed.'

config_parser = ConfigParser({ 'here': os.path.dirname(config_file) })
config_parser.read(config_file)

site_url = config_parser.get('app:main', 'ckan.site_url')
assert site_url

api_key = config_parser.get('app:main', 'ckanext.publicamundi.tests.api_key')
assert api_key

client = ckanapi.RemoteCKAN(site_url)
client.apikey = api_key

def setup_module():
    print ' ** Setup ** '

def teardown_module():
    print ' ** Teardown ** '

# Tests

@nose.tools.istest
def test_package_show():
    
    package_ids = client.action.package_list()
    
    for pid in package_ids:
        yield _test_package_show, pid

@nose.tools.istest
def test_package_list():
    
    d = client.action.package_list()
    assert isinstance(d, list)
    print ' -- Packages -- '
    print json.dumps(d, indent=4)

@nose.tools.istest
def test_package_create():
    
    data = {
        'dataset_type': 'foo',
        'name': 'test-hello-foo-1',
        'title': u'Test - Hello Foo (1)',
    } 
    yield _test_package_create, data
     
    data = {
        'name': 'test-hello-ckan-1',
        'title': u'Test - Hello CKAN (1)',
    } 
    yield _test_package_create, data
  
    data = {
        'dataset_type': 'boo',
        'name': 'test-hello-boo-1',
        'title': u'Test - Hello Boo (1)',
    } 
    yield _test_package_create_invalid, data, ['dataset_type']

def _test_package_show(name_or_id):
    
    d = client.action.package_show(id=name_or_id)
    
    print ' -- Package %s -- ' %(name_or_id)
    print json.dumps(d, indent=4)

def _test_package_create(data):
    
    d = client.action.package_create(**data)

def _test_package_create_invalid(data, bad_fields):
    
    ex = None
    try:
        d = client.action.package_create(**data)
    except ValidationError as ex1:
        ex = ex1
    
    assert ex
    assert all([k in ex.error_dict for k in bad_fields])

if __name__ == '__main__':
    _test_package_list('hello-baz-3')

