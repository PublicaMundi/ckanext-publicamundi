import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata.types import *

if __name__  == '__main__':
    x1 = InspireMetadata(
        foo='bar', 
        title=u'Ababoua', 
        tags=['a','b'], 
        url='http://example.com'
    )
    x1.validate()
