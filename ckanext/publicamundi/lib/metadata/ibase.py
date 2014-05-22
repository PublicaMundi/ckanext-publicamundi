import zope.interface 
import zope.schema

import ckanext.publicamundi.lib

class IBaseObject(zope.interface.Interface):
    
    def get_validation_errors():
        '''Invoke all validators and return a dict with errors.'''
    
    def validate_invariants():
        '''Invoke all object-level validators (invariants). 
        On failure, an exception is raised.'''

    def validate():
        '''Validate object (both field-level and object-level).
        Raises an exception on the 1st error encountered.'''

    def to_dict(flatten):
        '''Convert to a (flattened or not) dict'''

