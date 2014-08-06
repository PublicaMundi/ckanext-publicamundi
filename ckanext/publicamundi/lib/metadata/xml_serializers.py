import datetime
import random
import re
import inflection
import zope.interface
import zope.schema
import zope.schema.interfaces
from lxml import etree
from lxml.etree import Element, ElementTree, QName

from ckanext.publicamundi.lib.util import raise_for_stub_method
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import \
    ISerializer, IXmlSerializer, IObject

__all__ = [
    'field_xml_serialize_adapter',
    'xml_serializer_for_field',
]

# Decorators for adaptation

def field_xml_serialize_adapter(required_iface):
    assert required_iface.isOrExtends(zope.schema.interfaces.IField)
    def decorate(cls):
        adapter_registry.register([required_iface], IXmlSerializer, 'serialize', cls)
        return cls
    return decorate

# Serializers

class BaseSerializer(object):
    zope.interface.implements(IXmlSerializer)
   
    nsmap = { 
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }

    # Interface IXmlSerializer

    def to_xsd(self, o=None):
        xsd_uri = self.nsmap['xs']
        e = Element(QName(xsd_uri, 'element'), attrib={
            'name': self.name
        })
        e1 = self._to_xsd_type()
        e.append(e1)
        return e
    
    def to_xml(self, obj):
        raise_for_stub_method()
    
    def from_xml(self, el):
        raise_for_stub_method
       
    def dumps(self, o):
        e = self.to_xml(o)
        return etree.tostring(e)

    def loads(self, s):
        el = etree.fromstring(s)
        assert el.tag == self.name
        return self.from_xml(el)

    # Helpers

    def _to_xsd_type(self):
        '''Build and return an XML tree representing the XSD type definition for 
        this field (e.g. an xs:complexType or an xs:simpleType). 
        '''
        raise_for_stub_method()

class BaseFieldSerializer(BaseSerializer):

    def __init__(self, field):
        self.field = field
        # Assign a name and a typename to this XSD type
        if field.context and hasattr(field.context, 'key'):
            self.name = inflection.dasherize(field.context.key)
        else: 
            name = field.getName()
            self.name = name if name else str(inflection.parameterize(field.title))
            self.name = inflection.dasherize(self.name)
        assert self.name
        self.typename = inflection.camelize(self.name)

@field_xml_serialize_adapter(zope.schema.interfaces.INativeString)
class StringSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        raise NotImplementedError('Todo')
    
    def to_xml(self, s):
        assert isinstance(s, str)
        el = Element(self.name)
        el.text = s.decode('utf-8')
        return el

    def from_xml(self, el):
        return el.text.encode('utf-8')

@field_xml_serialize_adapter(zope.schema.interfaces.IChoice)
class ChoiceSerializer(StringSerializer):
    
    def to_xsd(self, o=None):
        raise NotImplementedError('Todo')
    
@field_xml_serialize_adapter(zope.schema.interfaces.IText)
@field_xml_serialize_adapter(zope.schema.interfaces.ITextLine)
class UnicodeSerializer(BaseFieldSerializer):

    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']

        # Create an xs:simpleType element

        e1 = Element(QName(xsd_uri, 'simpleType'))
        e11 = Element(QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:string'
        })
        e1.append(e11)

        # Put restrictions on length

        if self.field.min_length:
            e11.append(Element(QName(xsd_uri, 'minLength'), attrib={
                'value': str(self.field.min_length),
            }))        
        if self.field.max_length:
            e11.append(Element(QName(xsd_uri, 'maxLength'), attrib={
                'value': str(self.field.max_length),
            }))

        # Put restrictions on pattern (if detected)
        # Note: The following is an attempt (just heuristics) to detect a
        # regex pattern given as a constraint (e.g. re.compile(p).match)
        
        fn = self.field.constraint
        if fn and hasattr(fn, '__self__'): 
            r = fn.__self__
            re1 = re.compile('a')
            if isinstance(r, type(re1)):
                pattern = r.pattern
                e11.append(Element(QName(xsd_uri, 'pattern'), attrib={
                    'value': pattern
                }))

        # Return definition
        return e1 
   
    def to_xml(self, u):
        assert isinstance(u, unicode)
        el = Element(self.name)
        el.text = u
        return el

    def from_xml(self, el):
        return el.text

@field_xml_serialize_adapter(zope.schema.interfaces.IInt)
class IntSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        raise NotImplementedError('Todo')
    
    def to_xml(self, n):
        assert isinstance(n, int)
        el = Element(self.name)
        el.text = str(n)
        return el

    def from_xml(self, el):
        return int(el.text)

@field_xml_serialize_adapter(zope.schema.interfaces.IBool)
class BoolSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        raise NotImplementedError('Todo')
    
    def to_xml(self, y):
        assert isinstance(y, bool)
        el = Element(self.name)
        el.text = 'true' if y else 'false'
        return el

    def from_xml(self, el):
        s = el.text
        if s is None:
            return None
        s = str(s).lower()
        # Use bool cast, except for string 'false'
        if s == 'false':
            return False
        else:
            return bool(s)

@field_xml_serialize_adapter(zope.schema.interfaces.IFloat)
class FloatSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        raise NotImplementedError('Todo')
    
    def to_xml(self, n):
        assert isinstance(n, float)
        el = Element(self.name)
        el.text = str(n)
        return el

    def from_xml(self, el):
        return float(el.text)

@field_xml_serialize_adapter(zope.schema.interfaces.IDatetime)
class DatetimeSerializer(BaseFieldSerializer):

    date_format = "%Y-%m-%d %H:%M:%S"
    
    def _to_xsd_type(self):
        raise NotImplementedError('Todo')
     
    def to_xml(self, t):
        assert isinstance(t, datetime.datetime)
        el = Element(self.name)
        el.text = t.strftime(self.date_format)
        return el

    def from_xml(self, el):
        s = str(el.text)
        t = datetime.datetime.strptime(s, self.date_format)
        return t

@field_xml_serialize_adapter(zope.schema.interfaces.IDate)
class DateSerializer(BaseFieldSerializer):

    date_format = "%Y-%m-%d"
    
    def _to_xsd_type(self):
        raise NotImplementedError('Todo')
     
    def to_xml(self, t):
        assert isinstance(t, datetime.date)
        el = Element(self.name)
        el.text = t.strftime(self.date_format)
        return el

    def from_xml(self, el):
        s = str(el.text)
        t = datetime.datetime.strptime(s, self.date_format)
        return t.date()

@field_xml_serialize_adapter(zope.schema.interfaces.ITime)
class TimeSerializer(BaseFieldSerializer):

    time_format = "%H:%M:%S"
    
    def _to_xsd_type(self):
        raise NotImplementedError('Todo')
     
    def to_xml(self, t):
        assert isinstance(t, datetime.time)
        el = Element(self.name)
        el.text = t.strftime(self.date_format)
        return el
    
    def from_xml(self, el):
        s = str(el.text)
        t = datetime.datetime.strptime(s, self.date_format)
        return t.time()

# Utilities

def xml_serializer_for_field(field):
    '''Get a proper XML serializer for a zope.schema.Field instance.
    ''' 
    assert isinstance(field, zope.schema.Field)
    serializer = adapter_registry.queryMultiAdapter([field], IXmlSerializer, 'serialize')
    return serializer

