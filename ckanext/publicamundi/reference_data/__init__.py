import os

here = os.path.dirname(__file__)

def get_path(relpath):
    path = os.path.join(here, relpath)
    if os.path.exists(path):
        return path
    else:
        raise ValueError('Path not found')

