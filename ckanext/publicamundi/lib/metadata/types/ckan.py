import zope.interface
import zope.schema

import ckanext.publicamundi.lib

from ckanext.publicamundi.lib.metadata.schema import ICkanMetadata

class CkanMetadata(object):
    zope.interface.implements(ICkanMetadata)

    def __init__(self):
        pass

