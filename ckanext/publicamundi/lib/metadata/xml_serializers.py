import random
import datetime
import isodate
import re
import inflection
import zope.interface
import zope.schema
import zope.schema.interfaces
from lxml import etree
from lxml.etree import \
    Element, SubElement, ElementTree, QName

from ckanext.publicamundi.lib.util import raise_for_stub_method
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import FieldContext
from ckanext.publicamundi.lib.metadata.ibase import \
    ISerializer, IXmlSerializer, IObject

__all__ = [
    'field_xml_serialize_adapter',
    'xml_serializer_for_field', 'xml_serializer_factory_for_field',
]

# Decorators for adaptation

def field_xml_serialize_adapter(required_iface):
    assert required_iface.isOrExtends(zope.schema.interfaces.IField)
    def decorate(cls):
        adapter_registry.register([required_iface], IXmlSerializer, 'serialize', cls)
        return cls
    return decorate

# Utilities

def serializer_for_field(field):
    '''Get an XML serializer for a zope.schema.Field instance.
    ''' 
    assert isinstance(field, zope.schema.Field)
    serializer = adapter_registry.queryMultiAdapter([field], IXmlSerializer, 'serialize')
    return serializer

def serializer_factory_for_field(field_iface):
    '''Get an XML serializer factory for a zope.schema.Field interface.
    ''' 
    assert field_iface.extends(zope.schema.interfaces.IField)
    factory = adapter_registry.lookup([field_iface], IXmlSerializer, 'serialize')
    return factory

xml_serializer_for_field = serializer_for_field

xml_serializer_factory_for_field = serializer_factory_for_field

# Serializers

class BaseSerializer(object):
    zope.interface.implements(IXmlSerializer)
   
    name = None

    nsmap = { 
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }

    # Interface IXmlSerializer

    target_namespace = None

    def to_xsd(self, o=None, wrap_into_schema=False):
        xsd_uri = self.nsmap['xs']

        e = Element(QName(xsd_uri, 'element'), attrib={
            'name': self.name
        })
        
        e.append(self._to_xsd_type())
        
        return e
    
    def to_xml(self, obj):
        el = Element(QName(self.target_namespace, self.name))
        self._to_xml(obj, el)
        return el
    
    def from_xml(self, el):
        qname = QName(el.tag)
        assert qname.localname == self.name and qname.namespace == self.target_namespace
        o = self._from_xml(el)
        return o
       
    def dumps(self, o):
        el = self.to_xml(o)
        s = etree.tostring(el, pretty_print=True, xml_declaration=True, encoding='utf-8')
        return s

    def loads(self, s):
        el = etree.fromstring(s)
        o = self.from_xml(el)
        return o

    # Implementation

    def _to_xsd_type(self):
        '''Build and return an XML tree representing the XSD type definition for 
        this field or object (e.g. an xs:complexType or an xs:simpleType). 
        '''
        raise_for_stub_method()
    
    def _to_xml(self, obj, el):
        '''Build the XML subtree under element el to serialize obj.
        '''
        raise_for_stub_method()

    def _from_xml(self, el):
        '''Build and return an object from XML subtree under element el. 
        '''
        raise_for_stub_method()

class BaseFieldSerializer(BaseSerializer):

    max_occurs = 1

    min_occurs = 1
    
    def __init__(self, field):
        self.field = field
        
        # Try to name this XSD type

        name = None

        if field.context and hasattr(field.context, 'key'):
            name = field.context.key
        else:
            name = field.getName() or str(inflection.parameterize(field.title))
            if not name:
                try:
                    name = field.getTaggedValue('name')
                except KeyError:
                    pass
        
        assert name, 'The field should be named'
            
        self.name = name = inflection.dasherize(name)
            
        # Compute occurence indicators
        # Note: A serializer may alter these values at any time, before 
        # calling to_xsd() method (e.g. for collection items).

        self.min_occurs = 1 if field.required else 0

        self.max_occurs = 1

    @property
    def typename(self):
        if self.name:
            return inflection.camelize(self.name)
        else:
            return None
    
    def to_xsd(self, o=None, wrap_into_schema=False):
        xsd_uri = self.nsmap['xs']
        
        # Create an xs:element element
        
        attrib = {
            'name': self.name,
        }    
        
        if not wrap_into_schema:
            # If not at root, assign occurence indicators
            attrib.update({    
                'minOccurs': str(self.min_occurs),
                'maxOccurs': str(self.max_occurs),
            })

        e = Element(QName(xsd_uri, 'element'), attrib=attrib)
        
        # Annotate with existing documentation

        if self.field.title or self.field.description:
            e1 = SubElement(e, QName(xsd_uri, 'annotation'))
            if self.field.title:
                e11 = SubElement(e1, QName(xsd_uri, 'appinfo'))
                e11.text = self.field.title
            if self.field.description:
                e12 = SubElement(e1, QName(xsd_uri, 'documentation'))
                e12.text = self.field.description

        # Append type definition

        e2 = self._to_xsd_type()
        e.append(e2)
        
        # Return either the definition element (el) or an xs:schema 
        # element wrapping it.
        
        if wrap_into_schema:
            t = Element(
                QName(xsd_uri, 'schema'), 
                nsmap = { 
                    'target': self.target_namespace,    
                }, 
                attrib = {
                    'targetNamespace': self.target_namespace,
                    'elementFormDefault': 'qualified',
                }
            )
            t.append(e)
            return t
        else:
            return e

@field_xml_serialize_adapter(zope.schema.interfaces.INativeString)
class StringFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']

        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:string'
        })

        # Put restrictions on length

        if self.field.min_length:
            e1.append(Element(QName(xsd_uri, 'minLength'), attrib={
                'value': str(self.field.min_length),
            }))        
        if self.field.max_length:
            e1.append(Element(QName(xsd_uri, 'maxLength'), attrib={
                'value': str(self.field.max_length),
            }))

        # Put restrictions with a pattern (if detected)
        
        e1p = self._build_xsd_restriction_with_pattern()
        if e1p is not None:
            e1.append(e1p)

        # Return definition
        return e

    def _build_xsd_restriction_with_pattern(self):
        
        # Note: The following is an attempt (just heuristics) to detect a
        # regex pattern given as a constraint (e.g. re.compile(p).match)
        
        fn = self.field.constraint
        if fn and hasattr(fn, '__self__'): 
            r = fn.__self__
            re1 = re.compile('a')
            if isinstance(r, type(re1)):
                xsd_uri = self.nsmap['xs']
                pattern = r.pattern
                pattern = pattern.lstrip('^')
                pattern = pattern.rstrip('$')
                el = Element(QName(xsd_uri, 'pattern'), attrib={ 'value': pattern })
                return el
        return None

    def _to_xml(self, s, el):
        assert isinstance(s, str)
        el.text = s.decode('utf-8')

    def _from_xml(self, el):
        return el.text.encode('utf-8')

@field_xml_serialize_adapter(zope.schema.interfaces.IChoice)
class ChoiceFieldSerializer(StringFieldSerializer):
     
    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']

        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:string'
        })

        # Enumerate possible values
        
        for t in self.field.vocabulary:
            e1.append(Element(QName(xsd_uri, 'enumeration'), attrib={
                'value': t.value
            }))
        
        return e
  
@field_xml_serialize_adapter(zope.schema.interfaces.IText)
@field_xml_serialize_adapter(zope.schema.interfaces.ITextLine)
class UnicodeFieldSerializer(StringFieldSerializer):

    def _to_xml(self, u, el):
        assert isinstance(u, unicode)
        el.text = u

    def _from_xml(self, el):
        return unicode(el.text)

@field_xml_serialize_adapter(zope.schema.interfaces.IInt)
class IntFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:integer'
        })
         
        # Put restrictions on range

        m = self.field.min
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'minInclusive'), attrib={
                'value': str(m),
            }))
        m = self.field.max
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'maxInclusive'), attrib={
                'value': str(m),
            }))
       
        return e
    
    def _to_xml(self, n, el):
        assert isinstance(n, int)
        el.text = str(n)

    def _from_xml(self, el):
        return int(el.text)

@field_xml_serialize_adapter(zope.schema.interfaces.IBool)
class BoolFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:boolean'
        })

        return e
    
    def _to_xml(self, y, el):
        assert isinstance(y, bool)
        el.text = 'true' if y else 'false'

    def _from_xml(self, el):
        s = el.text
        if s is None:
            return None
        s = str(s).lower()
        if s == 'false':
            return False
        elif s == 'true':
            return True
        else:
            return None

@field_xml_serialize_adapter(zope.schema.interfaces.IFloat)
class FloatFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:float'
        })
        
        # Put restrictions on range
        # Note: Are inclusive limits meaningfull in floats ?

        m = self.field.min
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'minExclusive'), attrib={
                'value': str(m),
            }))
        m = self.field.max
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'maxExclusive'), attrib={
                'value': str(m),
            }))

        return e
   
    def _to_xml(self, n, el):
        assert isinstance(n, float)
        el.text = str(n)

    def _from_xml(self, el):
        return float(el.text)

@field_xml_serialize_adapter(zope.schema.interfaces.IDatetime)
class DatetimeFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:dateTime'
        })
        
        # Put restrictions on range

        m = self.field.min
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'minExclusive'), attrib={
                'value': m.isoformat(),
            }))
        m = self.field.max
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'maxExclusive'), attrib={
                'value': m.isoformat(),
            }))

        return e

    def _to_xml(self, t, el):
        assert isinstance(t, datetime.datetime)
        el.text = t.isoformat()

    def _from_xml(self, el):
        s = str(el.text)
        d = isodate.parse_datetime(s)
        return d

@field_xml_serialize_adapter(zope.schema.interfaces.IDate)
class DateFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:date'
        })
        
        # Put restrictions on range

        m = self.field.min
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'minExclusive'), attrib={
                'value': m.isoformat(),
            }))
        m = self.field.max
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'maxExclusive'), attrib={
                'value': m.isoformat(),
            }))

        return e
    
    def _to_xml(self, t, el):
        assert isinstance(t, datetime.date)
        el.text = t.isoformat()

    def _from_xml(self, el):
        s = str(el.text)
        d = isodate.parse_date(s)
        return d

@field_xml_serialize_adapter(zope.schema.interfaces.ITime)
class TimeFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:time'
        })
        
        # Put restrictions on range

        m = self.field.min
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'minExclusive'), attrib={
                'value': m.isoformat(),
            }))
        m = self.field.max
        if m is not None:
            e1.append(Element(QName(xsd_uri, 'maxExclusive'), attrib={
                'value': m.isoformat(),
            }))

        return e
    
    def _to_xml(self, t, el):
        assert isinstance(t, datetime.time)
        el.text = t.isoformat()
    
    def _from_xml(self, el):
        s = str(el.text)
        t = isodate.parse_time(s)
        return t

@field_xml_serialize_adapter(zope.schema.interfaces.IList)
class ListFieldSerializer(BaseFieldSerializer):

    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:complexType element

        e = Element(QName(xsd_uri, 'complexType'))
        e1 = SubElement(e, QName(xsd_uri, 'sequence'))
        
        yf = self.field.value_type

        ser = serializer_for_field(yf)
        ser.target_namespace = self.target_namespace
        ser.min_occurs = self.field.min_length
        ser.max_occurs = self.field.max_length

        e1.append(ser.to_xsd())
       
        return e
    
    def _to_xml(self, l, el):
        assert isinstance(l, list) or isinstance(l, tuple)
        
        yf = self.field.value_type
        ser = serializer_for_field(yf)
        ser.target_namespace = self.target_namespace
       
        for y in l:
            el.append(ser.to_xml(y))
    
    def _from_xml(self, el):
        l = list()
        
        yf = self.field.value_type
        ser = serializer_for_field(yf)
        ser.target_namespace = self.target_namespace
        
        for p in el:
            l.append(ser.from_xml(p))
        
        return l

@field_xml_serialize_adapter(zope.schema.interfaces.IDict)
class DictFieldSerializer(BaseFieldSerializer):

    def _to_xsd_type(self):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:complexType element

        e = Element(QName(xsd_uri, 'complexType'))
        e1 = SubElement(e, QName(xsd_uri, 'sequence'))
        
        yf = self.field.value_type

        ser = serializer_for_field(yf)
        ser.target_namespace = self.target_namespace
        ser.max_occurs = 'unbounded'

        e1.append(ser.to_xsd())
       
        return e
    
    def _to_xml(self, d, el):
        assert isinstance(d, dict)
        
        raise NotImplementedError('Todo')

        #yf = self.field.value_type
        #ser = serializer_for_field(yf)
        #ser.target_namespace = self.target_namespace
       
        #for y in l:
        #    el.append(ser.to_xml(y))
    
    def _from_xml(self, el):
        d = dict()
        
        raise NotImplementedError('Todo')
        
        #yf = self.field.value_type
        #ser = serializer_for_field(yf)
        #ser.target_namespace = self.target_namespace
        
        #for p in el:
        #    l.append(ser.from_xml(p))
        
        return d

