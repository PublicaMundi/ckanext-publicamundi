import zope.interface
import zope.schema

class ISerializer(zope.interface.Interface):

    def loads(s, opts=None):
        '''Load (unserialize) and return an object from a string
        '''

    def dumps(obj, opts=None):
        '''Dump (serialize) an object as a string
        '''

class IXmlSerializer(ISerializer):

    def xsd(obj, opts=None):
        '''Generate an XML Schema document (XSD) for a given object
        '''

class ISerializable(zope.interface.Interface):

    def loads(s, opts=None):
        '''Load (unserialize) this object from a string
        '''

    def dumps(opts=None):
        '''Dump (serialize) this object as a string
        '''

class IObject(zope.interface.Interface):

    def schema():
        '''Return the schema interface (InterfaceClass) this object is supposed to
        conform to.'''

    def get_field(k):
        '''Return the zope.schema.Field that corresponds to attribute k.
        The returned field instance should be bound to the context of this object.
        '''

    def validate():
        '''Invoke all validators and return a list structured as
            <errors> ::= [ (<field>, <field-errors>), ... ]
            <field-errors> ::= [ <ex-1>, ... ]
        The invariants (keyed at None) are checked only if schema validation (field-based) succeeds.
        '''

    def to_dict(flat, opts={}):
        '''Convert to a (flattened or nested) dict.
        This method should *not* alter the object itself.
        '''

    def from_dict(d, is_flat=None, opts={}):
        '''Load this object from a (flattened or nested) dict.
        If parameter is_flat is not provided, an input dict d with tuple-typed keys will be
        considered a flattened dict (otherwise, will be considered a nested one).
        '''

    def to_json(flat, indent):
        '''Convert to a (flattened or nested) JSON dump.
        This method should *not* alter the object itself.
        '''

    def from_json(s, is_flat):
        '''Load this object from a (flattened or nested) JSON dump.
        Note that (unlike from_dict()) an explicit flag (is_flat) should be passed to
        determine if input should be considered as flattened/nested.
        '''
    
    def to_xsd(opts={}):
        '''Generate an XML schema definition (XSD) for this class.
        '''
    
    def to_xml(opts={}):
        '''Convert to XML.
        This method should *not* alter the object itself.
        '''
    
    def from_xml(xml, opts={}):
        '''Load this object from an XML dump.
        '''

class IErrorDict(zope.interface.Interface):

    global_key = zope.schema.ASCII(
        required = True,
        default = None,
        description = u'A key that denotes an error not specific to a field (i.e. global)')

    def get(key=None):
        '''Get error info for a field keyed at param key.
        A key of None should fetch global (non field-specific) errors.

        This method should return 
         - an IErrorDict-compatible object, if key represents a non-leaf field
         - a list of error strings, if key represents a leaf field or the global key 
         - None, if nothing is found at key 
        '''

    def keys():
        '''Return a list of available keys (including the global one, if that exists).
        '''
