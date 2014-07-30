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
args = argp.parse_args()

application = loadapp('config:%s' %(args.config_file));

testapp = TestApp(application)

res = testapp.get(args.path)

print res
