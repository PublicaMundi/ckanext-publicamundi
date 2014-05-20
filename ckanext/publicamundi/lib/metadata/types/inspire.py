import zope.interface
import zope.schema

import ckanext.publicamundi.lib

from ckanext.publicamundi.lib.metadata.schema import IInspireMetadata

class InspireMetadata(object):
    zope.interface.implements(IInspireMetadata)

    def __init__(self):
        pass

