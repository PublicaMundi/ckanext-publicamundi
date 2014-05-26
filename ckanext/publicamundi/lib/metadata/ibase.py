import zope.interface 

class ISerializer(zope.interface.Interface):
    
    def loads(s, opts=None):
        '''Load (unserialize) an object a string
        '''
    
    def dumps(obj, opts=None):
        '''Dump (serialize) an object as a string
        '''

class IBaseObject(zope.interface.Interface):
    
    def schema():
        '''Return the schema interface (InterfaceClass) this object is supposed to
        conform to.'''

    def validate():
        '''Invoke all validators and return a list structured as 
            <errors> ::= [ (<field>, <field-errors>), ... ]
            <field-errors> ::= [ <ex-1>, ... ]
        The invariants (keyed at None) are checked only if schema validation (field-based) succeeds.
        '''

    def to_dict(flat):
        '''Convert to a (flattened or nested) dict.
        This method should *not* alter the object itself.
        '''
    
    def from_dict(d, is_flat=None):
        '''(Re)construct this object from a (flattened or nested) dict. 
        If parameter is_flat is not provided, an input dict d with tuple-typed keys will be 
        considered a flattened dict (otherwise, will be considered a nested one).
        '''

    def to_json(flat, indent):
        '''Convert to a (flattened or nested) JSON dump.
        This method should *not* alter the object itself.
        '''
    
    def from_json(s, is_flat):
        '''(Re)construct this object from a (flattened or nested) JSON dump.
        Note that (unlike from_dict()) an explicit flag (is_flat) should be passed to 
        determine if input should be considered as flattened/nested.
        '''


