#!/usr/bin/env python

import os.path
import sys

from paste.deploy import loadapp
from wsgiref.simple_server import make_server

here = os.path.dirname(os.path.realpath(__file__))

config_file = None

if len(sys.argv) > 1:
    config_file = sys.argv[1] 
else: 
    config_file = os.path.join(here, 'development.ini')

application = loadapp('config:%s' %(config_file));

if __name__ == '__main__':
    httpd = make_server('127.0.0.1', 8000, application)
    print 'Serving at 127.0.0.1:8000 ...'
    httpd.serve_forever()
