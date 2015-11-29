from functools import wraps

from pylons import (c, request, response)
from pylons.controllers.util import (abort, redirect)

def authenticated(action):   
    @wraps(action)
    def wrap_action(self, *args, **kwargs):
        if not c.userobj:
            abort(401)
        return action(self, *args, **kwargs)
    return wrap_action

