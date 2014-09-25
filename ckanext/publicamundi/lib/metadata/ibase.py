import zope.interface
import zope.schema

class ISerializer(zope.interface.Interface):

    def loads(s):
        '''Load (unserialize) and return an object from a string.
        '''

    def dumps(obj=None):
        '''Dump (serialize) an object as a string.

        If obj is None, the object to be serialized is inferred from
        context (e.g. an adaptee object).
        '''

class IKeyTupleSerializer(ISerializer):

    prefix = zope.schema.NativeString(required=False)
    
    glue = zope.schema.NativeString(required=True, default='.')
    
    def get_key_predicate(key_type, strict=False):
        '''Get a predicate function that checks if a given key is valid 
        for the certain serializer and the certain key_type.  
        '''

class IXmlSerializer(ISerializer):
    
    target_namespace = zope.schema.URI(required = True)
    
    name = zope.schema.NativeString(required=True)

    typename = zope.schema.NativeString(required=True)

    def to_xsd(wrap_into_schema=False, type_prefix='', annotate=False):
        '''Generate an XML Schema document (XSD) for the XML documents 
        that this serializer generates.
        
        If wrap_into_schema is True, a valid xs:schema element tree 
        should be returned.
        Otherwise, a tuple of (<el>, <tdefs>) should be returned, where: 
            - <el>: is the xs:element element tree that describes structure.
            - <tdefs>: is a mapping of { <type-name>: <type-def> } that contains type 
              definitions (e.g. xs:simpleType or xs:complexType) that element <el> 
              depends on and should be placed at the global scope (as global 
              type definitions).

        If type_prefix is given, it will prefix (i.e. qualify) all global type 
        definitions generated. This is usefull to avoid type-name conflicts.
        '''
    
    def to_xml(o=None, nsmap=None):
        '''Dump a given object o to an XML tree.

        If o is None, the object to be serialized is inferred from context 
        (e.g. can be an adaptee object).

        If nsmap is a mapping { <alias>: <namespace> } , it will be used to override 
        default namespace aliases.
        '''

    def from_xml(e):
        '''Load and return an object from an XML tree e.
        '''

class ISerializable(zope.interface.Interface):

    def loads(s):
        '''Load (unserialize) this object from a string.
        '''

    def dumps():
        '''Dump (serialize) this object as a string.
        '''

class IFormatSpec(zope.interface.Interface):

    name = zope.schema.NativeString(required=True)

    opts = zope.schema.Dict(required=False, 
        key_type = zope.schema.NativeString(),
        value_type = zope.schema.Field())

    def parse(s):
        '''Parse this format-spec as a string'''

class IFormatter(zope.interface.Interface):
    
    requested_name = zope.schema.NativeString(required=True)
    
    def format(value=None, opts={}):
        '''Format the given value as a unicode string. 
        If no value is supplied, the formatter should try a meaningfull guess
        from it's context.
        '''

class IObject(zope.interface.Interface):

    def get_schema():
        '''Return the schema interface (InterfaceClass) this object is supposed to
        conform to.
        '''

    def get_field(k):
        '''Return a bound zope.schema.Field instance that corresponds to key k.

        This method should regard k as:
            * an attribute k, if k is a string.
            * a path of attributes/keys, if k is a tuple
        '''
    
    def get_fields(exclude_properties=False):
        '''Return a map of fields.
        '''

    def iter_fields(exclude_properties=False):
        '''Return an iterator on (name, field).
        '''
   
    def get_flattened_fields(opts={}):
        '''Return a flat map of fields.
        '''
    
    def validate(dictize_errors=False):
        '''Invoke all validators and return errors. 
        The invariants are checked only if schema validation (field-based) succeeds. 
        
        If dictize_errors is False, a list is returned structured as: 
            <errors> ::= [ (<field>, <field-errors>), ... ]
            <field-errors> ::= [ <ex-1>, ... ]

        If dictize_errors is True, a dict is returned with keys corresponding to
        fields.
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

class IErrorDict(zope.interface.Interface):

    global_key = zope.schema.NativeString(
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
