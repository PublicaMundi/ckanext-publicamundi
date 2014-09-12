import json
import webtest
import nose.tools
import inflection
import logging

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

    def test_create_package(self):
        
        yield self._create_package, 'hello-foo-1'
        
    def _create_package(self, pkg_name):
        
        pkg_dict = package_fixtures[pkg_name] 
        assert pkg_dict['name'] == pkg_name

        res1 = self.app.get('/dataset/new', status='*')
        assert res1.status == 200
        
        dt = pkg_dict.get('dataset_type', 'ckan')
        dt_spec = dataset_types[dt]
        key_prefix = dt_spec.get('key_prefix', dt)

        # 1st stage
    
        form1 = res1.forms['package-form'] 
        for k in ['title', 'name', 'dataset_type', 'notes', 'license_id']:
            form1.set(k, pkg_dict.get(k))
        form1.set('tag_string', ','.join(map(lambda t: t['name'], pkg_dict.get('tags', []))))
        
        res1s = form1.submit('save')
        assert res1s.status in [301, 302] 
        
        # 2nd stage

        res2 = res1s.follow()
        
        resource_dict = next(iter(pkg_dict['resources'])) # 1st resource
        form2 = res2.forms['resource-form']
        for k in ['description', 'url', 'name', 'format']:
            form2.set(k, resource_dict.get(k))
        
        btns = form2.fields.get('save')
        i2 = next(j for j, b in enumerate(btns) if b.id == 'btn-save-go-metadata')
        res2s = form2.submit('save', index=i2, status='*')
        assert res2s.status in [301, 302]

        # 3rd stage - core metadata

        res3 = res2s.follow()
        
        form3 = res3.forms['package-form']
        for k in ['version', 'url', 'author', 'author_email', 'maintainer', 'maintainer_email']:
            form3.set(k, pkg_dict.get(k))

        # 3rd stage - dataset_type-related metadata

        for t, v in dictization.flatten(pkg_dict.get(dt)).items():
            k = '.'.join((key_prefix,) + t)
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
        
        res5 = self.app.get('/api/action/package_show?id=%s' %(pkg_name))
        assert res5.json.get('success')
        
        res_dict = res5.json.get('result')
        print json.dumps(res_dict, indent=4)

        assert res_dict['dataset_type'] == dt
        
        for k in (self.basic_fields & set(res_dict.keys())):
            assert res_dict[k] == pkg_dict[k]
        
        pkg_dt_dict = dictization.flatten(pkg_dict.get(dt))
        res_dt_dict = dictization.flatten(res_dict.get(dt))
        for k in pkg_dt_dict.keys():
            assert res_dt_dict[k] == pkg_dt_dict[k]

        assert False

## Fixtures ##

package_fixtures = {
    'hello-foo-1': {
        'title': u'Hello Foo (1)',
        'name': 'hello-foo-1',
        'notes': u'I am the first _Foo_ dataset!',
        'author': u'Nowhere Man',
        'license_id': 'gfdl',
        'version': '1.0.0',
        'maintainer': u'Nowhere Man',
        'author_email': 'nowhere-man@example.com',
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
            'created': u'2014-09-13 17:00:00',
            'temporal_extent': { 
                'start': '2012-01-01',
                'end': '2013-01-01',
            },
            'thematic_category': 'health',
        },
        'resources': [
            {
                'url': 'http://example.com/res/1',
                'name': u'Example 1',
                'format': 'HTML',
                'description': u'A very important HTML document',
            },
        ],
    },
}
