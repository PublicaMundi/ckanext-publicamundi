import zope.interface
import zope.schema
import logging

import ckanext.publicamundi.lib

from ckanext.publicamundi.lib.metadata.schema import ICkanMetadata
from ckanext.publicamundi.lib.metadata.schema import IInspireMetadata

class CkanMetadata(object):
    zope.interface.implements(ICkanMetadata)

    def __init__(self):
        pass

class InspireMetadata(object):
    zope.interface.implements(IInspireMetadata)

    def __init__(self):
        pass

