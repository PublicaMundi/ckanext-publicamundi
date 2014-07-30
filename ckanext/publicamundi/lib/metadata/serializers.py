import datetime
import zope.interface
import zope.schema

from ckanext.publicamundi.lib.metadata.ibase import ISerializer

class BaseSerializer(object):
    zope.interface.implements(ISerializer)

    def dumps(self, o):
        return str(o)

    def loads(self, s):
        return str(s)

class StringSerializer(BaseSerializer):

    def dumps(self, s):
        assert isinstance(s, basestring)
        return str(s)

    def loads(self, s):
        return str(s)

class UnicodeSerializer(BaseSerializer):

    def __init__(self, encoding='unicode-escape'):
        self.encoding = encoding

    def dumps(self, u):
        assert isinstance(u, unicode)
        return u.encode(self.encoding)

    def loads(self, s):
        return s.decode(self.encoding)

class IntSerializer(BaseSerializer):

    def dumps(self, n):
        assert isinstance(n, int)
        return str(n)

    def loads(self, s):
        return int(s)

class LongSerializer(BaseSerializer):

    def dumps(self, n):
        assert isinstance(n, long)
        return str(n)

    def loads(self, s):
        return long(s)

class BoolSerializer(BaseSerializer):

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

class FloatSerializer(BaseSerializer):

    def dumps(self, f):
        assert isinstance(f, float)
        return str(f)

    def loads(self, s):
        return float(s)

class DatetimeSerializer(BaseSerializer):

    def __init__(self, fmt="%Y-%m-%d %H:%M:%S"):
        self.fmt = fmt

    def dumps(self, t):
        assert isinstance(t, datetime.datetime)
        return t.strftime(self.fmt)

    def loads(self, s):
        return datetime.datetime.strptime(s, self.fmt)

class DateSerializer(BaseSerializer):

    def __init__(self, fmt="%Y-%m-%d"):
        self.fmt = fmt

    def dumps(self, t):
        assert isinstance(t, datetime.date)
        return t.strftime(self.fmt)

    def loads(self, s):
        t = datetime.datetime.strptime(s, self.fmt)
        return t.date()

class TimeSerializer(BaseSerializer):

    def __init__(self, fmt="%H:%M:%S"):
        self.fmt = fmt

    def dumps(self, t):
        assert isinstance(t, datetime.time)
        return t.strftime(self.fmt)

    def loads(self, s):
        t = datetime.datetime.strptime(s, self.fmt)
        return t.time()

class KeyTupleSerializer(object):

    def __init__(self, glue, prefix, suffix):
        self.glue = str(glue)
        self.prefix = str(prefix or '')
        self.suffix = str(suffix or '')

    def dumps(self, l):
        assert isinstance(l, tuple) or isinstance(l, list)
        s = self.prefix
        s += self.glue.join(map(str, l))
        s += self.suffix
        return s

    def loads(self, s):
        if not s.startswith(self.prefix) or not s.endswith(self.suffix):
            raise ValueError('The dump is malformed')
        if self.prefix:
            s = s[len(self.prefix):]
        if self.suffix:
            s = s[:-len(self.suffix)]
        l = tuple(str(s).split(self.glue))
        return l

# Todo
# A better way to map fields to their serializers would be through
# the existing adapter registry (provide the ISerializer interface)

_field_serializers = {
    zope.schema.TextLine: UnicodeSerializer(),
    zope.schema.Text: UnicodeSerializer(),
    zope.schema.BytesLine: None,
    zope.schema.Bytes: None,
    zope.schema.Int: IntSerializer(),
    zope.schema.Float: FloatSerializer(),
    zope.schema.Bool: BoolSerializer(),
    zope.schema.Datetime: DatetimeSerializer(),
    zope.schema.Date: DateSerializer(),
    zope.schema.Time: TimeSerializer(),
    zope.schema.DottedName: StringSerializer(),
    zope.schema.URI: StringSerializer(),
    zope.schema.Id: StringSerializer(),
    zope.schema.Choice: None,
    zope.schema.List: None,
    zope.schema.Tuple: None,
    zope.schema.Dict: None,
}

# Todo
# Maybe name as serializer_for() to provide similar naming with other
# adapters

def get_key_tuple_serializer(glue):
    '''Get a proper serializer for a dict tuple-typed key
    '''
    return KeyTupleSerializer(glue, prefix=None, suffix=None)

def get_key_string_serializer():
    '''Get a proper serializer for a dict str-typed key
    '''
    return StringSerializer()

def get_field_serializer(F):
    '''Get a proper serializer for a leaf zope.schema.Field instance
    ''' 
    
    # Note:
    # Consider using F.fromUnicode as an unserializer.
    
    assert isinstance(F, zope.schema.Field)
    serializer = _field_serializers.get(type(F))
    return serializer

