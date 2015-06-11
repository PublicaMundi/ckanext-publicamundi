#!/usr/bin/env python

import os.path
import argparse
import sys

from paste.deploy import loadapp
from webtest import TestApp, Upload

here = os.path.dirname(os.path.realpath(__file__))

argp = argparse.ArgumentParser()
argp.add_argument("inputs", nargs=1, type=str)
argp.add_argument("-c", "--config", dest='config_file', type=str,
    default=os.environ['CKAN_CONFIG'])
argp.add_argument("-u", "--user", dest='remote_user', type=str, 
    default='admin')
argp.add_argument("-o", "--owner-org", dest='owner_org', type=str,
    default='acme')
argp.add_argument("-t", "--dataset-type", dest='dataset_type', type=str, 
    default='inspire')
args = argp.parse_args()

app = loadapp('config:%s' %(args.config_file));
testapp = TestApp(app)

extra_environ = {}
if args.remote_user:
    extra_environ['REMOTE_USER'] = args.remote_user

metadata_file = os.path.realpath(args.inputs[0])
metadata = None 
with open(metadata_file, 'r') as ifp:
    metadata = ifp.read()

res = testapp.post('/dataset/import_metadata', 
    { 
        'dataset_type': args.dataset_type, 
        'owner_org': args.owner_org,
        'rename': 'y',
        'force_create': 'n',
        'source-upload': Upload(os.path.basename(metadata_file), metadata),
    },
    extra_environ=extra_environ)

