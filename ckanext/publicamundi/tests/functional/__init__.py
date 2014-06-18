import functools
import nose.tools
import pylons

import ckan.tests
from ckan.tests import url_for

def setup_request_context(response):
    ''' Setup Pylons globals (c, url request, response, session)
    for an emulated request.

    Args:
        response is the response from an instance of webtest.TestApp

    '''
    pylons.tmpl_context._push_object(response.tmpl_context)
    pylons.request._push_object(response.req)
    pylons.response._push_object(response.response)
    pylons.session._push_object(response.session)
    pylons.url._push_object(response.req.path)

def teardown_request_context():
    '''Teardown Pylons globals (c, url, request, response, session)
    '''
    pylons.tmpl_context._pop_object()
    pylons.request._pop_object()
    pylons.response._pop_object()
    pylons.session._pop_object()
    pylons.url._pop_object()

def with_request_context(route_name, action='index'):
    def _decorator(method):
        @functools.wraps(method)
        def _method(test_controller, *args, **kwargs):
            if not (isinstance(test_controller, ckan.tests.TestController)):
                raise TypeError('The decorated can only be applied to a TestController')
            resp = test_controller.app.get(url_for(route_name, action=action))
            setup_request_context(resp)
            try:
                method(test_controller, *args, **kwargs)
            finally:
                teardown_request_context()
        return _method
    return _decorator

