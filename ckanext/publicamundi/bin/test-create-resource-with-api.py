#!/usr/bin/env python

import os
import argparse
import hashlib
import json
import mimetypes
from urlparse import urlparse
from paste.deploy import loadapp, appconfig
from webtest import TestApp, Upload

here = os.path.dirname(os.path.realpath(__file__))

argp = argparse.ArgumentParser()
argp.add_argument("inputs", metavar='RESOURCE', nargs=1);
argp.add_argument("-c", "--config", dest='config_file', default=os.environ['CKAN_CONFIG']);
argp.add_argument("-u", "--user", dest='remote_user', default='admin');
argp.add_argument("-H", "--host", dest='host');
argp.add_argument("-f", "--format", dest='format');
argp.add_argument("-m", "--mimetype", dest='mimetype');
argp.add_argument("-p", "--package", dest='package_ref');
argp.add_argument("-t", "--description", dest='description', 
    help=u'Provide description for resource');
argp.add_argument("-n", "--name", dest='name',
    help=u'Provide a human-readable for the resource');
args = argp.parse_args()

app = loadapp('config:%s' %(args.config_file))
testapp = TestApp(app)

app_conf = appconfig('config:%s' %(args.config_file))

host = args.host
if not host:
    site_url = app_conf.get('ckan.site_url')
    if site_url:
        host = urlparse(site_url).netloc
    else:
        host = os.environ.get('HOSTNAME', 'localhost')

headers = {
    'Host': host,
}

extra_environ = {}
if args.remote_user:
    extra_environ['REMOTE_USER'] = args.remote_user

infile = args.inputs[0]
with open(infile, 'r') as ifp:
    contents = ifp.read()

mimetype = args.mimetype
if not mimetype:
    mimetype, encoding = mimetypes.guess_type(infile)

data = { 
    'package_id': args.package_ref,
    'format': args.format,
    'name': args.name,
    'hash': hashlib.sha1(contents).hexdigest(),
    'mimetype': mimetype,
    'size': '%s' % len(contents),
    'description': args.description or args.name,
    'upload': Upload(os.path.basename(infile), contents)
}

res = testapp.post('/api/action/resource_create', data, headers=headers, extra_environ=extra_environ)

result = res.json['result']
print json.dumps(result)
