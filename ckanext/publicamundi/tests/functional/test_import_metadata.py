# -*- encoding: utf-8 -*-

import logging
import os
import nose.tools
import json
import webtest

import ckan.tests
from ckan.tests import url_for

class TestController(ckan.tests.TestController):

    action_url_args = {
        'controller': 'ckanext.publicamundi.controllers.package:Controller', 
        'action': 'import_metadata'
    }
    
    create_as_user = 'tester'  # Todo: Create at setup
    owner_org = 'acme'         # Todo: Create at setup, add `create_as_user` as editor
    
    samples_dir = './tests/samples'

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
        metadata = None
        with open(metadata_file, 'r') as ifp:
            metadata = ifp.read()

        res = self.app.post(target_url, 
            { 
                'dataset_type': 'inspire', 
                'owner_org': self.owner_org,
                'rename': 'y',
                'force_create': 'n',
                'source-upload': webtest.Upload(os.path.basename(metadata_file), metadata),
            },
            extra_environ={ 
                'REMOTE_USER': self.create_as_user,
            })


        # Todo: Assert a package with expected identifier is created
        
        pass
        
