# -*- encoding: utf-8 -*-

import logging
import os
import nose.tools
import json
from collections import OrderedDict
import webtest
from webtest import Upload

import ckan.tests
from ckan.tests import url_for
from ckan.tests import CreateTestData

class TestController(ckan.tests.TestController):

    action_url_args = {
        'controller': 'ckanext.publicamundi.controllers.package:Controller', 
        'action': 'import_metadata'
    }
    
    owner_org = { 
        'name': u'acme',
        'title': u'Acme Corporation',
        'description': u'A fictional organization',
    }

    samples_dir = './tests/samples'
    
    @classmethod
    def setup_class(cls):
        
        logging.basicConfig(level=logging.INFO)

        CreateTestData.create_user('tester', about='A tester', password='tester')
        CreateTestData.create_groups([
            {
                'name': cls.owner_org['name'],
                'title':  cls.owner_org['title'],
                'description': cls.owner_org['description'],
                'type': 'organization',
                'is_organization': True,
            }], admin_user_name='tester')
        
        cls.extra_environ = {'REMOTE_USER': 'tester'}
        
        return

    @classmethod
    def teardown_class(cls):
        pass

    @nose.tools.istest
    def test_inspire(self):
        
        sample_files = [
            '11786ee2-828a-4513-9117-7d3b1dc93b7b.xml', # Orthophotos - Greece
            '57d0f331-6950-4deb-a2f6-30e560915a2e.xml', # Corine-2000 - Greece
            'd59c2895-49c0-416f-a77e-122459cc8cac.xml', # Coastline - Greece
        ]
        
        for metadata_file in sample_files:
            yield self._test_inspire_metadata_with_upload, metadata_file

    def _test_inspire_metadata_with_upload(self, metadata_file):
        target_url = url_for(**self.action_url_args)        
        
        metadata_file = os.path.realpath(os.path.join(self.samples_dir, metadata_file))
        metadata_fname = os.path.basename(metadata_file)
        metadata = None
        with open(metadata_file, 'r') as ifp:
            metadata = ifp.read()
        
        params = OrderedDict((
            ('dataset_type', 'inspire'),
            ('owner_org', self.owner_org['name']),
            ('rename', 'n'),
            ('force_create', 'n'),
        ))
        res = self.app.post(target_url, 
            params = params, 
            upload_files = [('source-upload', metadata_fname, metadata)], 
            extra_environ = self.extra_environ)
        assert res.status in [301, 302]

        # Assert a package with expected identifier is created

        identifier = os.path.splitext(metadata_fname)[0] 
        res = self.app.get('/api/action/dataset_show',
            params = {'id': identifier}, status=200)
        
        assert res.json
        r = res.json['result']
        assert r['id'] == identifier
        assert r['dataset_type'] == 'inspire'
        assert ('inspire' in r) and (r['inspire']['identifier'] == identifier)
