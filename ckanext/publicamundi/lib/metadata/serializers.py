'''Provide serializers for leaf zope.schema fields

We provide named adapters for ISerializer interface. These adapters are named 
according to their serialization formats (as "serialize:<fmt>").
These serializers are str-based, i.e. they always dump to plain str (not unicode).

So far, the formats supported are:

    * default: 
        Provide basic methods for all leaf fields.
    
    * input: 
        Provide methods needed to load/dump field values from/to web requests.
        The "input" serializers are mostly needed to decode (i.e. loads) values 
        from request.param. For the sake of completeness, we also provide the inverse
        operation (dumps).
    
    * json-s: 
        Provide methods to load/dump field values to a JSON-serializable format
        understood by json.dumps. This kind of serializer will *not* be registered to
        handle data types inherently supported by JSON (e.g. like integers and floats).

Note that for a specific format and a field interface, a serializer may not exist:
this is not an error, it usually means that serialization is not meaningfull in this 
context (and maybe values should be left unchanged, see examples below).

For example, as integers dont need to be serialized to be understood by JSON:
    
    >>> f = zope.schema.Int(title=u'height')
    >>> ser = serializer_for_field(f, fmt='json-s')
    >>> assert ser is None 

Of course, if instead we asked for a `default` serializer, we should get one:
    
    >>> f = zope.schema.Int(title='height')
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
import zope.schema.interfaces
from itertools import chain

from ckanext.publicamundi.lib.util import raise_for_stub_method
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import \
    IObject, ISerializer, IKeyTupleSerializer

__all__ = [
    'supported_formats',
    'field_serialize_adapter', 
    'object_serialize_adapter',
    'BaseSerializer', 
    'serializer_for_key_tuple', 
    'serializer_for_field',
    'serializer_factory_for_key_tuple', 
    'serializer_factory_for_field',
]

# Decorators for adaptation

supported_formats = [ 'default', 'input', 'json-s' ]

def field_serialize_adapter(required_iface, fmt='default'):
    assert required_iface.isOrExtends(zope.schema.interfaces.IField)
    assert fmt in supported_formats
    name = 'serialize:%s' % (fmt)
    def decorate(cls):
        adapter_registry.register([required_iface], ISerializer, name, cls)
        return cls
    return decorate

def object_serialize_adapter(required_iface, fmt='default'):
    assert required_iface.isOrExtends(IObject)
    assert fmt in supported_formats
    name = 'serialize:%s' % (fmt)
    def decorate(cls):
        adapter_registry.register([required_iface], ISerializer, name, cls)
        return cls
    return decorate

def key_tuple_serialize_adapter():
    def decorate(cls):
        adapter_registry.register([], IKeyTupleSerializer, 'serialize-key', cls)
        return cls
    return decorate

# Utilities

def serializer_for_key_tuple():
    '''Get a proper serializer for the tuple-typed keys of a dict.
    '''
    serializer = adapter_registry.queryMultiAdapter([], IKeyTupleSerializer, 'serialize-key')
    return serializer

def serializer_for_field(field, fmt='default'):
    '''Get a proper serializer for a zope.schema.Field instance.
    Normally, this will be used for leaf (non collection-based) fields.
    ''' 
    assert isinstance(field, zope.schema.Field)
    assert fmt in supported_formats
    name = 'serialize:%s' % (fmt)
    serializer = adapter_registry.queryMultiAdapter([field], ISerializer, name)
    return serializer

def serializer_factory_for_key_tuple():
    '''Get a proper serializer factory for the tuple-typed keys of a dict.
    '''
    factory = adapter_registry.lookup([], ISerializer, 'serialize-key')
    return factory

def serializer_factory_for_field(field_iface, fmt='default'):
    '''Get a proper serializer factory for a zope.schema.Field interface.
    ''' 
    assert field_iface.extends(zope.schema.interfaces.IField)
    assert fmt in supported_formats
    name = 'serialize:%s' % (fmt)
    factory = adapter_registry.lookup([field_iface], ISerializer, name)
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
        return self._to_string(o)

    def loads(self, s):
        assert isinstance(s, basestring)
        return self._from_string(s)

    # Implementation

    def _to_string(self, o):
        raise_for_stub_method()

    def _from_string(self, s):
        raise_for_stub_method()

@field_serialize_adapter(zope.schema.interfaces.INativeString, fmt='default')
@field_serialize_adapter(zope.schema.interfaces.IChoice, fmt='default')
@field_serialize_adapter(zope.schema.interfaces.INativeString, fmt='json-s')
@field_serialize_adapter(zope.schema.interfaces.IChoice, fmt='json-s')
class StringFieldSerializer(BaseFieldSerializer):
    
    def _to_string(self, s):
        assert isinstance(s, basestring)
        return str(s)

    def _from_string(self, s):
        return str(s)

@field_serialize_adapter(zope.schema.interfaces.IText, fmt='default')
@field_serialize_adapter(zope.schema.interfaces.ITextLine, fmt='default')
class UnicodeFieldSerializer(BaseFieldSerializer):

    encoding = 'unicode-escape'

    def _to_string(self, u):
        assert isinstance(u, unicode)
        return u.encode(self.encoding)

    def _from_string(self, s):
        if isinstance(s, unicode):
            return s
        else:
            return str(s).decode(self.encoding)

@field_serialize_adapter(zope.schema.interfaces.IText, fmt='input')
@field_serialize_adapter(zope.schema.interfaces.ITextLine, fmt='input')
class UnicodeInputFieldSerializer(UnicodeFieldSerializer):

    encoding = 'utf-8'

    pass

@field_serialize_adapter(zope.schema.interfaces.IInt, fmt='default')
@field_serialize_adapter(zope.schema.interfaces.IInt, fmt='input')
class IntFieldSerializer(BaseFieldSerializer):

    def _to_string(self, n):
        assert isinstance(n, int)
        return str(n)

    def _from_string(self, s):
        return int(s)

@field_serialize_adapter(zope.schema.interfaces.IBool, fmt='default')
class BoolFieldSerializer(BaseFieldSerializer):

    def _to_string(self, y):
        assert isinstance(y, bool)
        return 'true' if y else 'false'

    def _from_string(self, s):
        if s is None:
            return None
        s = str(s).lower()
        # Use bool cast, except for string 'false'
        if s == 'false':
            return False
        else:
            return bool(s)

@field_serialize_adapter(zope.schema.interfaces.IBool, fmt='input')
class BoolInputFieldSerializer(BaseFieldSerializer):
    
    def _to_string(self, y):
        assert isinstance(y, bool)
        flag_name = self.field.getName() or 'true'
        return flag_name if y else ''

    def _from_string(self, s):
        if s is None:
            return None
        return bool(s)

@field_serialize_adapter(zope.schema.interfaces.IFloat, fmt='default')
@field_serialize_adapter(zope.schema.interfaces.IFloat, fmt='input')
class FloatFieldSerializer(BaseFieldSerializer):

    def _to_string(self, f):
        assert isinstance(f, float)
        return str(f)

    def _from_string(self, s):
        return float(s)

@field_serialize_adapter(zope.schema.interfaces.IDatetime, fmt='default')
@field_serialize_adapter(zope.schema.interfaces.IDatetime, fmt='json-s')
class DatetimeFieldSerializer(BaseFieldSerializer):
   
    def _to_string(self, t):
        assert isinstance(t, datetime.datetime)
        return t.isoformat()

    def _from_string(self, s):
        return isodate.parse_datetime(s) 

@field_serialize_adapter(zope.schema.interfaces.IDatetime, fmt='input')
class DatetimeFormattedFieldSerializer(BaseFieldSerializer):

    fmt = "%Y-%m-%d %H:%M:%S"
   
    def _to_string(self, t):
        assert isinstance(t, datetime.datetime)
        return t.strftime(self.fmt)

    def _from_string(self, s):
        return datetime.datetime.strptime(s, self.fmt)

@field_serialize_adapter(zope.schema.interfaces.IDate, fmt='default')
@field_serialize_adapter(zope.schema.interfaces.IDate, fmt='json-s')
class DateFieldSerializer(BaseFieldSerializer):
    
    def _to_string(self, t):
        assert isinstance(t, datetime.date)
        return t.isoformat()

    def _from_string(self, s):
        return isodate.parse_date(s)

@field_serialize_adapter(zope.schema.interfaces.IDate, fmt='input')
class DateFormattedFieldSerializer(BaseFieldSerializer):

    fmt = "%Y-%m-%d"
    
    def _to_string(self, t):
        assert isinstance(t, datetime.date)
        return t.strftime(self.fmt)

    def _from_string(self, s):
        t = datetime.datetime.strptime(s, self.fmt)
        return t.date()

@field_serialize_adapter(zope.schema.interfaces.ITime, fmt='default')
@field_serialize_adapter(zope.schema.interfaces.ITime, fmt='json-s')
class TimeFieldSerializer(BaseFieldSerializer):

    def _to_string(self, t):
        assert isinstance(t, datetime.time)
        return t.isoformat()

    def _from_string(self, s):
        return isodate.parse_time(s)

@field_serialize_adapter(zope.schema.interfaces.ITime, fmt='input')
class TimeFormattedFieldSerializer(BaseFieldSerializer):

    fmt = "%H:%M:%S"

    def _to_string(self, t):
        assert isinstance(t, datetime.time)
        return t.strftime(self.fmt)

    def _from_string(self, s):
        t = datetime.datetime.strptime(s, self.fmt)
        return t.time()

@key_tuple_serialize_adapter()
class KeyTupleSerializer(BaseSerializer):

    zope.interface.implements(IKeyTupleSerializer)
    
    glue = '.'
    
    _prefix = None

    @property
    def prefix(self):
        return self._prefix 
    
    @prefix.setter
    def prefix(self, value):
        if value is not None:
            assert isinstance(value, str) and value.find(self.glue) < 0
            self._prefix = value

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

