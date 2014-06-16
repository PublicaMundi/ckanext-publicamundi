#!/usr/bin/env python

import os.path
import sys

from paste.deploy import loadapp
from webtest import TestApp

here = os.path.dirname(os.path.realpath(__file__))

config_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'development.ini')

application = loadapp('config:%s' %(config_file));
