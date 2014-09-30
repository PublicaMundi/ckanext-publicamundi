'''Provide serializers for leaf zope.schema fields

We provide named adapters for ISerializer interface. These adapters are named 
according to their serialization formats (as "serialize:<name>").
These serializers are str-based, i.e. they always dump to plain str (not unicode).

So far, the formats supported are:

    * default: 
        Provide basic methods for all leaf fields.
    
    * json-s: 
        Provide methods to load/dump field values to a JSON-serializable format
        understood by json.dumps. This kind of serializer will *not* be registered to
        handle data types inherently supported by JSON (e.g. like integers and floats).

Note that for a specific format and a field interface, a serializer may not exist:
this is not an error, it usually means that serialization is not meaningfull in this 
context (and maybe values should be left unchanged, see examples below).

For example, as integers dont need to be serialized to be understood by JSON:
    
    >>> f = zope.schema.Int(title=u'height')
    >>> ser = serializer_for_field(f, name='json-s')
    >>> assert ser is None 

Of course, if instead we asked for a `default` serializer, we should get one:
    
    >>> f = zope.schema.Int(title=u'height')
    >>> ser = serializer_for_field(f)
    >>> assert ser
    >>> assert ser.dumps(5) == '5'
     
'''

import datetime
import isodate
import re
import pickle
import zope.interface
import zope.schema
from itertools import chain

from ckanext.publicamundi.lib.util import raise_for_stub_method
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import ISerializer, IKeyTupleSerializer

__all__ = [
    'supported_formats',
    'field_serialize_adapter',
    'BaseSerializer', 
    'serializer_for_key_tuple', 
    'serializer_for_field',
    'serializer_factory_for_key_tuple', 
    'serializer_factory_for_field',
]

# Decorators for adaptation

supported_formats = [ 'default', 'json-s' ]

def field_serialize_adapter(required_iface, name='default'):
    assert required_iface.isOrExtends(IField)
    assert name in supported_formats
    def decorate(cls):
        adapter_registry.register(
            [required_iface], ISerializer, 'serialize:%s' %(name), cls)
        return cls
    return decorate

def key_tuple_serialize_adapter():
    def decorate(cls):
        adapter_registry.register([], IKeyTupleSerializer, 'serialize-key', cls)
        return cls
    return decorate

# Utilities

def serializer_for_key_tuple(key_prefix=None):
    '''Get a proper serializer for the tuple-typed keys of a dict.
    '''
    serializer = adapter_registry.queryMultiAdapter([], IKeyTupleSerializer, 'serialize-key')
    if key_prefix is not None:
        serializer.prefix = key_prefix
    return serializer

def serializer_for_field(field, name='default'):
    '''Get a proper serializer for a zope.schema.Field instance.
    Normally, this will be used for leaf (non collection-based) fields.
    ''' 
    assert isinstance(field, zope.schema.Field)
    assert name in supported_formats
    serializer = adapter_registry.queryMultiAdapter(
        [field], ISerializer, 'serialize:%s' %(name))
    return serializer

def serializer_factory_for_key_tuple():
    '''Get a proper serializer factory for the tuple-typed keys of a dict.
    '''
    factory = adapter_registry.lookup([], ISerializer, 'serialize-key')
    return factory

def serializer_factory_for_field(field_iface, name='default'):
    '''Get a proper serializer factory for a zope.schema.Field interface.
    ''' 
    assert field_iface.extends(IField)
    assert name in supported_formats
    factory = adapter_registry.lookup(
        [field_iface], ISerializer, 'serialize:%s' %(name))
    return factory

# Serializers

class BaseSerializer(object):
    
    zope.interface.implements(ISerializer)
    
    def dumps(self, o=None):
        return pickle.dumps(o)

    def loads(self, s):
        return pickle.loads(s)

class BaseFieldSerializer(BaseSerializer):
    
    def __init__(self, field):
        self.field = field
    
    # Interface ISerializer
    
    def dumps(self, o=None):
        if o is None:
            o = self.field.context.value
        return self._to(o)

    def loads(self, s):
        assert isinstance(s, basestring)
        return self._from(s)

    # Implementation

    def _to(self, o):
        raise_for_stub_method()

    def _from(self, s):
        raise_for_stub_method()

@field_serialize_adapter(IStringField, 'default')
@field_serialize_adapter(IChoiceField, 'default')
@field_serialize_adapter(IStringField, 'json-s')
@field_serialize_adapter(IChoiceField, 'json-s')
class StringFieldSerializer(BaseFieldSerializer):
    
    def _to(self, s):
        assert isinstance(s, basestring)
        return str(s)

    def _from(self, s):
        return str(s)

@field_serialize_adapter(ITextField, 'default')
@field_serialize_adapter(ITextLineField, 'default')
class UnicodeFieldSerializer(BaseFieldSerializer):

    encoding = 'unicode-escape'

    def _to(self, u):
        assert isinstance(u, unicode)
        return u.encode(self.encoding)

    def _from(self, s):
        if isinstance(s, unicode):
            return s
        else:
            return str(s).decode(self.encoding)

@field_serialize_adapter(IIntField, 'default')
class IntFieldSerializer(BaseFieldSerializer):

    def _to(self, n):
        assert isinstance(n, int)
        return str(n)

    def _from(self, s):
        return int(s)

@field_serialize_adapter(IBoolField, 'default')
class BoolFieldSerializer(BaseFieldSerializer):

    def _to(self, y):
        assert isinstance(y, bool)
        return 'true' if y else 'false'

    def _from(self, s):
        if s is None:
            return None
        s = str(s).lower()
        # Use bool cast, except for string 'false'
        if s == 'false':
            return False
        else:
            return bool(s)

@field_serialize_adapter(IFloatField, 'default')
class FloatFieldSerializer(BaseFieldSerializer):

    def _to(self, f):
        assert isinstance(f, float)
        return str(f)

    def _from(self, s):
        return float(s)

@field_serialize_adapter(IDatetimeField, 'default')
@field_serialize_adapter(IDatetimeField, 'json-s')
class DatetimeFieldSerializer(BaseFieldSerializer):
   
    def _to(self, t):
        assert isinstance(t, datetime.datetime)
        return t.isoformat()

    def _from(self, s):
        t = None
        try:
            t = isodate.parse_datetime(s)
        except ValueError:
            pass
        if not t:
            t = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
        return t

@field_serialize_adapter(IDateField, 'default')
@field_serialize_adapter(IDateField, 'json-s')
class DateFieldSerializer(BaseFieldSerializer):
    
    def _to(self, t):
        assert isinstance(t, datetime.date)
        return t.isoformat()

    def _from(self, s):
        t = None
        try:
            t = isodate.parse_date(s)
        except ValueError:
            pass
        if not t:
            t = datetime.datetime.strptime(s, '%Y-%m-%d')
            t = t.date()
        return t

@field_serialize_adapter(ITimeField, 'default')
@field_serialize_adapter(ITimeField, 'json-s')
class TimeFieldSerializer(BaseFieldSerializer):

    def _to(self, t):
        assert isinstance(t, datetime.time)
        return t.isoformat()

    def _from(self, s):
        t = None
        try:
            t = isodate.parse_time(s)
        except ValueError:
            pass
        if not t:
            t = datetime.datetime.strptime(s, '%H:%M:%S')
            t = t.time()
        return t

@key_tuple_serialize_adapter()
class KeyTupleSerializer(BaseSerializer):

    zope.interface.implements(IKeyTupleSerializer)
    
    glue = '.'
    
    _prefix = None

    def get_key_predicate(self, key_type, strict=False):        
        if not self._prefix:
            return lambda k: True
        elif issubclass(key_type, basestring):
            p = self._prefix + self.glue
            if strict:
                return lambda k: isinstance(k, key_type) and k.startswith(p)
            else:
                return lambda k: k.startswith(p)                
        elif key_type is tuple:
            p = self._prefix
            if strict:
                return lambda k: isinstance(k, key_type) and k and k[0] == p
            else:
                return lambda k: k and k[0] == p
           
    @property
    def prefix(self):
        return self._prefix 
    
    @prefix.setter
    def prefix(self, value):
        if value is not None:
            assert isinstance(value, basestring) and value.find(self.glue) < 0
            self._prefix = str(value)

    def dumps(self, l):
        assert isinstance(l, tuple) or isinstance(l, list)
        q = chain([self._prefix], l) if self._prefix else iter(l)
        return self.glue.join(map(str, q))

    def loads(self, s):
        q = str(s).split(self.glue)
        if self._prefix:
            prefix = q.pop(0)
            if not prefix == self._prefix:
                raise ValueError('The key dump is malformed')
        return tuple(q)

