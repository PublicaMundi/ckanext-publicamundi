#!/usr/bin/env python

import sys
import json
import time
import urlparse

from wsgiref.simple_server import make_server

def application(environ, start_response):

    result = {}
    
    qs = urlparse.parse_qs(environ['QUERY_STRING'])

    # Build a Celery-compliant webhook response 

    if not 'fail' in qs:
        result['status'] = 'success'
        result['retval'] = { 'query-string': qs, 'path': environ['PATH_INFO'] }
    else:
        result['status'] = 'failure'
        result['reason'] = 'Failed to do something'

    start_response('200 OK', [('Content-type', 'application/json')])
    return [json.dumps(result)]

if __name__ == '__main__':
    host = str(sys.argv[1])
    port = int(sys.argv[2])
    httpd = make_server(host, port, application)
    print "Serving HTTP  at %s:%d..." %(host, port)
    httpd.serve_forever()

