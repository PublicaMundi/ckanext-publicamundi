import datetime
import pickle
import zope.interface
import zope.schema
import zope.schema.interfaces

from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import ISerializer, IObject

__all__ = [
    'field_serialize_adapter', 'object_serialize_adapter',
    'BaseSerializer', 
    'serializer_for_key_tuple', 'serializer_for_field',
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
        adapter_registry.register([], ISerializer, 'serialize:key', cls)
        return cls
    return decorate

# Serializers

class BaseSerializer(object):
    zope.interface.implements(ISerializer)
    
    def dumps(self, o):
        return pickle.dumps(o)

    def loads(self, s):
        return pickle.loads(s)

class BaseFieldSerializer(BaseSerializer):
    
    def __init__(self, field):
        self.field = field
    
    def dumps(self, o):
        return str(o)

    def loads(self, s):
        return str(s)

@field_serialize_adapter(zope.schema.interfaces.INativeString)
@field_serialize_adapter(zope.schema.interfaces.IChoice)
class StringSerializer(BaseFieldSerializer):
    
    def dumps(self, s):
        assert isinstance(s, basestring)
        return str(s)

    def loads(self, s):
        return str(s)

@field_serialize_adapter(zope.schema.interfaces.IText)
@field_serialize_adapter(zope.schema.interfaces.ITextLine)
class UnicodeSerializer(BaseFieldSerializer):

    encoding = 'unicode-escape'

    def dumps(self, u):
        assert isinstance(u, unicode)
        return u.encode(self.encoding)

    def loads(self, s):
        return s.decode(self.encoding)

@field_serialize_adapter(zope.schema.interfaces.IInt)
class IntSerializer(BaseFieldSerializer):

    def dumps(self, n):
        assert isinstance(n, int)
        return str(n)

    def loads(self, s):
        return int(s)

@field_serialize_adapter(zope.schema.interfaces.IBool)
class BoolSerializer(BaseFieldSerializer):

    def dumps(self, y):
        assert isinstance(y, bool)
        return 'true' if y else 'false'

    def loads(self, s):
        if s is None:
            return None
        s = str(s).lower()
        # Use bool cast, except for string 'false'
        if s == 'false':
            return False
        else:
            return bool(s)

@field_serialize_adapter(zope.schema.interfaces.IFloat)
class FloatSerializer(BaseFieldSerializer):

    def dumps(self, f):
        assert isinstance(f, float)
        return str(f)

    def loads(self, s):
        return float(s)

@field_serialize_adapter(zope.schema.interfaces.IDatetime)
class DatetimeSerializer(BaseFieldSerializer):

    fmt = "%Y-%m-%d %H:%M:%S"
   
    def dumps(self, t):
        assert isinstance(t, datetime.datetime)
        return t.strftime(self.fmt)

    def loads(self, s):
        return datetime.datetime.strptime(s, self.fmt)

@field_serialize_adapter(zope.schema.interfaces.IDate)
class DateSerializer(BaseFieldSerializer):

    fmt = "%Y-%m-%d"
    
    def dumps(self, t):
        assert isinstance(t, datetime.date)
        return t.strftime(self.fmt)

    def loads(self, s):
        t = datetime.datetime.strptime(s, self.fmt)
        return t.date()

@field_serialize_adapter(zope.schema.interfaces.ITime)
class TimeSerializer(BaseFieldSerializer):

    fmt = "%H:%M:%S"

    def dumps(self, t):
        assert isinstance(t, datetime.time)
        return t.strftime(self.fmt)

    def loads(self, s):
        t = datetime.datetime.strptime(s, self.fmt)
        return t.time()

@key_tuple_serialize_adapter()
class KeyTupleSerializer(BaseSerializer):

    glue = '.'
    
    prefix = ''
    
    suffix = ''

    def dumps(self, l):
        assert isinstance(l, tuple) or isinstance(l, list)
        s = self.prefix
        s += self.glue.join(map(str, l))
        s += self.suffix
        return s

    def loads(self, s):
        if not s.startswith(self.prefix) or not s.endswith(self.suffix):
            raise ValueError('The key dump is malformed')
        if self.prefix:
            s = s[len(self.prefix):]
        if self.suffix:
            s = s[:-len(self.suffix)]
        l = tuple(str(s).split(self.glue))
        return l

# Utilities

def serializer_for_key_tuple():
    '''Get a proper serializer for the tuple-typed keys of a dict.
    '''
    serializer = adapter_registry.queryMultiAdapter([], ISerializer, 'serialize:key')
    return serializer

def serializer_for_field(field):
    '''Get a proper serializer for a zope.schema.Field instance.
    Normally, this will be used for leaf (non collection-based) fields.
    ''' 
    assert isinstance(field, zope.schema.Field)
    serializer = adapter_registry.queryMultiAdapter([field], ISerializer, 'serialize')
    return serializer

