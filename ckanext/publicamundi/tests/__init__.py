
class MockTmplContext(object):
    def __init__(self):
        self.environ = {
            'pylons.routes_dict': {'controller': 'package'}
        }

class MockRequest(object):
    def __init__(self):
        self.params = {}

