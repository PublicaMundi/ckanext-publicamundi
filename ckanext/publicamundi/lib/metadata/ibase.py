import zope.interface 

class IBaseObject(zope.interface.Interface):
    
    def schema():
        '''Return the schema interface (InterfaceClass) this object is supposed to
        conform to.'''

    def validate():
        '''Invoke all validators and return a dict with errors.
        The invariants are checked only if schema validation (field-based) succeeds.
        Returns a list of errors.'''

    def to_dict(flat):
        '''Convert to a (flattened or nested) dict.
        This method should alter the object itself.'''
    
    def from_dict(d):
        '''(Re)construct this object from a (flattened or nested) dict. 
        A input dict with str-typed keys is considered a normal (nested) dict. 
        Unlike, a dict with tuple-typed keys is considered a flattened one.'''


