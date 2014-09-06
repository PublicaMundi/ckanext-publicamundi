import datetime
import pickle
import itertools
import zope.interface
import zope.schema
import zope.schema.interfaces
from itertools import chain

from ckanext.publicamundi.lib.util import raise_for_stub_method
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import \
    IObject, ISerializer, IKeyTupleSerializer

__all__ = [
    'field_serialize_adapter', 
    'object_serialize_adapter',
    'BaseSerializer', 
    'serializer_for_key_tuple', 
    'serializer_for_field',
    'serializer_factory_for_key_tuple', 
    'serializer_factory_for_field',
]

# Decorators for adaptation

def field_serialize_adapter(required_iface):
    assert required_iface.isOrExtends(zope.schema.interfaces.IField)
    def decorate(cls):
        adapter_registry.register([required_iface], ISerializer, 'serialize', cls)
        return cls
    return decorate

def object_serialize_adapter(required_iface):
    assert required_iface.isOrExtends(IObject)
    def decorate(cls):
        adapter_registry.register([required_iface], ISerializer, 'serialize', cls)
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

def serializer_for_field(field):
    '''Get a proper serializer for a zope.schema.Field instance.
    Normally, this will be used for leaf (non collection-based) fields.
    ''' 
    assert isinstance(field, zope.schema.Field)
    serializer = adapter_registry.queryMultiAdapter([field], ISerializer, 'serialize')
    return serializer

def serializer_factory_for_key_tuple():
    '''Get a proper serializer factory for the tuple-typed keys of a dict.
    '''
    factory = adapter_registry.lookup([], ISerializer, 'serialize-key')
    return factory

def serializer_factory_for_field(field_iface):
    '''Get a proper serializer factory for a zope.schema.Field interface.
    ''' 
    assert field_iface.extends(zope.schema.interfaces.IField)
    factory = adapter_registry.lookup([field_iface], ISerializer, 'serialize')
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

@field_serialize_adapter(zope.schema.interfaces.INativeString)
@field_serialize_adapter(zope.schema.interfaces.IChoice)
class StringFieldSerializer(BaseFieldSerializer):
    
    def _to_string(self, s):
        assert isinstance(s, basestring)
        return str(s)

    def _from_string(self, s):
        return str(s)

@field_serialize_adapter(zope.schema.interfaces.IText)
@field_serialize_adapter(zope.schema.interfaces.ITextLine)
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

@field_serialize_adapter(zope.schema.interfaces.IInt)
class IntFieldSerializer(BaseFieldSerializer):

    def _to_string(self, n):
        assert isinstance(n, int)
        return str(n)

    def _from_string(self, s):
        return int(s)

@field_serialize_adapter(zope.schema.interfaces.IBool)
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

@field_serialize_adapter(zope.schema.interfaces.IFloat)
class FloatFieldSerializer(BaseFieldSerializer):

    def _to_string(self, f):
        assert isinstance(f, float)
        return str(f)

    def _from_string(self, s):
        return float(s)

@field_serialize_adapter(zope.schema.interfaces.IDatetime)
class DatetimeFieldSerializer(BaseFieldSerializer):

    fmt = "%Y-%m-%d %H:%M:%S"
   
    def _to_string(self, t):
        assert isinstance(t, datetime.datetime)
        return t.strftime(self.fmt)

    def _from_string(self, s):
        return datetime.datetime.strptime(s, self.fmt)

@field_serialize_adapter(zope.schema.interfaces.IDate)
class DateFieldSerializer(BaseFieldSerializer):

    fmt = "%Y-%m-%d"
    
    def _to_string(self, t):
        assert isinstance(t, datetime.date)
        return t.strftime(self.fmt)

    def _from_string(self, s):
        t = datetime.datetime.strptime(s, self.fmt)
        return t.date()

@field_serialize_adapter(zope.schema.interfaces.ITime)
class TimeFieldSerializer(BaseFieldSerializer):

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

