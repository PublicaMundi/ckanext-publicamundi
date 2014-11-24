#!/usr/bin/env python

import os.path
import argparse
import sys

from paste.deploy import loadapp
from webtest import TestApp

here = os.path.dirname(os.path.realpath(__file__))

argp = argparse.ArgumentParser()
argp.add_argument("path", metavar='PATH', type=str, nargs='?', default='/')
argp.add_argument("-c", "--config", dest='config_file', type=str,
    default=os.path.join(here, 'development.ini'));
argp.add_argument("-u", "--user", dest='remote_user', type=str);
args = argp.parse_args()

app = loadapp('config:%s' %(args.config_file));

extra_environ = {}

if args.remote_user:
    extra_environ['REMOTE_USER'] = args.remote_user

testapp = TestApp(app)

res = testapp.get(args.path, extra_environ=extra_environ)

print res
