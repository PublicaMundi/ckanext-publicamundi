import zope.interface 
import zope.schema

import ckanext.publicamundi.lib

class IBaseObject(zope.interface.Interface):
    
    def get_validation_errors():
        '''Invoke all validators and return a dict with errors.'''

    def to_dict(flat):
        '''Convert to a (flattened or nested) dict'''

