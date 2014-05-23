import zope.interface 
import zope.schema

import ckanext.publicamundi.lib

class IBaseObject(zope.interface.Interface):
    
    def get_validation_errors():
        '''Invoke all validators and return a dict with errors.
        The invariants are checked only if schema validation (field-based) 
        is successfull'''

    def to_dict(flat):
        '''Convert to a (flattened or nested) dict.'''
    
    def from_dict(d):
        '''Construct from a (flattened or nested) dict. 
        A input dict with str-typed keys is considered a normal (nested) dict. 
        Unlike, a dict with tuple-typed keys is considered a flattened one.'''

