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

from ckanext.publicamundi.lib.util import raise_for_stub_method, random_name
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
    
    max_occurs = 1

    min_occurs = 1

    nsmap = { 
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }

    # Interface IXmlSerializer

    target_namespace = None

    def to_xsd(self, o=None, wrap_into_schema=False, type_prefix=''):
        xsd_uri = self.nsmap['xs']

        e = Element(QName(xsd_uri, 'element'), attrib={
            'name': self.name
        })
        
        e1, defs = self._to_xsd_type(type_prefix)

        e.append(e1)
        
        if wrap_into_schema:
            root = Element(
                QName(xsd_uri, 'schema'), 
                nsmap = { 
                    'target': self.target_namespace,    
                }, 
                attrib = {
                    'targetNamespace': self.target_namespace,
                    'elementFormDefault': 'qualified',
                }
            )
            for t in defs:
                root.append(t)
            root.append(e)
            return root
        else:
            return (e, defs)
    
    def to_xml(self, obj):
        e = Element(QName(self.target_namespace, self.name))
        self._to_xml(obj, e)
        return e
    
    def from_xml(self, e):
        qname = QName(e.tag)
        assert qname.localname == self.name and qname.namespace == self.target_namespace
        o = self._from_xml(e)
        return o
       
    def dumps(self, o):
        e = self.to_xml(o)
        s = etree.tostring(e, pretty_print=True, xml_declaration=True, encoding='utf-8')
        return s

    def loads(self, s):
        e = etree.fromstring(s)
        o = self.from_xml(e)
        return o

    # Properties

    @property
    def typename(self):
        return inflection.camelize(self.name)
    
    # Implementation

    def _to_xsd_type(self, type_prefix):
        '''Build an XML tree representing the XSD type definition for 
        this field or object (e.g. an xs:complexType or an xs:simpleType).
        This method always returns a tuple of (el, defs)
        '''
        raise_for_stub_method()
    
    def _to_xml(self, obj, e):
        '''Build the XML subtree under element e to serialize object obj.
        '''
        raise_for_stub_method()

    def _from_xml(self, e):
        '''Build and return an object from XML subtree under element e. 
        '''
        raise_for_stub_method()

class BaseFieldSerializer(BaseSerializer):
    
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
    
    def to_xsd(self, o=None, wrap_into_schema=False, type_prefix=''):
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

        e2, e2_defs = self._to_xsd_type(type_prefix)
        e.append(e2)
        
        # Decide what to return depending on wrap_into_schema flag
        
        if wrap_into_schema:
            root = Element(
                QName(xsd_uri, 'schema'), 
                nsmap = { 
                    'target': self.target_namespace,    
                }, 
                attrib = {
                    'targetNamespace': self.target_namespace,
                    'elementFormDefault': 'qualified',
                }
            )
            for t in e2_defs:
                root.append(t)
            root.append(e)
            return root
        else:
            return (e, e2_defs)

@field_xml_serialize_adapter(zope.schema.interfaces.INativeString)
class StringFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
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

        return (e, [])

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
                e = Element(QName(xsd_uri, 'pattern'), attrib={ 'value': pattern })
                return e
        return None

    def _to_xml(self, s, e):
        assert isinstance(s, str)
        e.text = s.decode('utf-8')

    def _from_xml(self, e):
        return e.text.encode('utf-8')

@field_xml_serialize_adapter(zope.schema.interfaces.IChoice)
class ChoiceFieldSerializer(StringFieldSerializer):
     
    def _to_xsd_type(self, type_prefix):
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
        
        return (e, [])
  
@field_xml_serialize_adapter(zope.schema.interfaces.IText)
@field_xml_serialize_adapter(zope.schema.interfaces.ITextLine)
class UnicodeFieldSerializer(StringFieldSerializer):

    def _to_xml(self, u, e):
        assert isinstance(u, unicode)
        e.text = u

    def _from_xml(self, e):
        return unicode(e.text)

@field_xml_serialize_adapter(zope.schema.interfaces.IInt)
class IntFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
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
       
        return (e, [])
    
    def _to_xml(self, n, e):
        assert isinstance(n, int)
        e.text = str(n)

    def _from_xml(self, e):
        return int(e.text)

@field_xml_serialize_adapter(zope.schema.interfaces.IBool)
class BoolFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:boolean'
        })

        return (e, [])
    
    def _to_xml(self, y, e):
        assert isinstance(y, bool)
        e.text = 'true' if y else 'false'

    def _from_xml(self, e):
        s = e.text
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
    
    def _to_xsd_type(self, type_prefix):
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

        return (e, [])
   
    def _to_xml(self, n, e):
        assert isinstance(n, float)
        e.text = str(n)

    def _from_xml(self, e):
        return float(e.text)

@field_xml_serialize_adapter(zope.schema.interfaces.IDatetime)
class DatetimeFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
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

        return (e, [])

    def _to_xml(self, t, e):
        assert isinstance(t, datetime.datetime)
        e.text = t.isoformat()

    def _from_xml(self, e):
        s = str(e.text)
        d = isodate.parse_datetime(s)
        return d

@field_xml_serialize_adapter(zope.schema.interfaces.IDate)
class DateFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
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

        return (e, [])
    
    def _to_xml(self, t, e):
        assert isinstance(t, datetime.date)
        e.text = t.isoformat()

    def _from_xml(self, e):
        s = str(e.text)
        d = isodate.parse_date(s)
        return d

@field_xml_serialize_adapter(zope.schema.interfaces.ITime)
class TimeFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
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

        return (e, [])
    
    def _to_xml(self, t, e):
        assert isinstance(t, datetime.time)
        e.text = t.isoformat()
    
    def _from_xml(self, e):
        s = str(e.text)
        t = isodate.parse_time(s)
        return t

@field_xml_serialize_adapter(zope.schema.interfaces.IList)
class ListFieldSerializer(BaseFieldSerializer):

    def _to_xsd_type(self, type_prefix):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:complexType element

        e = Element(QName(xsd_uri, 'complexType'))
        e1 = SubElement(e, QName(xsd_uri, 'sequence'))
        
        yf = self.field.value_type

        ys = serializer_for_field(yf)
        ys.target_namespace = self.target_namespace
        ys.min_occurs = self.field.min_length
        ys.max_occurs = self.field.max_length

        ys_prefix = '_'.join((type_prefix, self.typename, 'Y'))
        ye, ye_defs = ys.to_xsd(type_prefix=ys_prefix)
        e1.append(ye)
      
        return (e, ye_defs)
    
    def _to_xml(self, l, e):
        assert isinstance(l, list) or isinstance(l, tuple)
        
        yf = self.field.value_type
        ys = serializer_for_field(yf)
        ys.target_namespace = self.target_namespace
       
        for y in l:
            e.append(ys.to_xml(y))
    
    def _from_xml(self, e):
        l = list()
        
        yf = self.field.value_type
        ys = serializer_for_field(yf)
        ys.target_namespace = self.target_namespace
        
        for p in e:
            l.append(ys.from_xml(p))
        
        return l

@field_xml_serialize_adapter(zope.schema.interfaces.IDict)
class DictFieldSerializer(BaseFieldSerializer):

    def _to_xsd_type(self, type_prefix):
        xsd_uri = self.nsmap['xs']
        xs = lambda name: QName(xsd_uri, name)

        # Create an xs:complexType element

        e = Element(xs('complexType'))
        e1 = SubElement(e, xs('sequence'))
        
        yf = self.field.value_type
        ys = serializer_for_field(yf)
        ys.target_namespace = self.target_namespace
        ys.max_occurs = 'unbounded'

        ys_prefix = '_'.join((type_prefix, self.typename, 'Y'))
        ye, ye_defs = ys.to_xsd(type_prefix=ys_prefix)    
        e1.append(ye)

        # Extend type for item's element (ye) to carry a "key" attribute
        
        defs = ye_defs
        
        kf = self.field.key_type
        ks = serializer_for_field(kf)
        ks.target_namespace = self.target_namespace
        
        ks_prefix = '_'.join((type_prefix, self.typename, 'K'))
        ke, ke_defs = ks.to_xsd(type_prefix=ks_prefix)
        kt = ke.find(xs('simpleType'))

        ae = Element(xs('attribute'), attrib={ 
            'name': ks.name,
            'use': 'required',
        })
        ae.append(kt)

        yt = ye.find(xs('complexType'))
        if yt is None:
            yt = ye.find(xs('simpleType'))
            # Handle an xs:simpleType definition
            yt.attrib['name'] = '_'.join((ys_prefix, ys.typename))
            # Move original xs:simpleType definition to the global scope
            ye.remove(yt)
            defs.append(yt)
            # Define a new xs:complexType based on yt type definition
            ye1 = SubElement(ye, xs('complexType'))
            ye11 = SubElement(ye1, xs('simpleContent'))
            ye111 = SubElement(ye11, xs('extension'), attrib={
                'base': 'target:' + yt.attrib['name'], 
            })
            ye111.append(ae)
        else:
            # Handle an xs:complexType definition
            yt.append(ae)

        return (e, defs)
    
    def _to_xml(self, d, e):
        assert isinstance(d, dict)

        yf = self.field.value_type
        ys = serializer_for_field(yf)
        ys.target_namespace = self.target_namespace
       
        kf = self.field.key_type
        ks = serializer_for_field(kf)
        ks.target_namespace = self.target_namespace
        
        for k, y in d.items():
            ye = ys.to_xml(y)
            ye.attrib[ks.name] = k
            e.append(ye)
    
    def _from_xml(self, e):
        d = dict()
        
        yf = self.field.value_type
        ys = serializer_for_field(yf)
        ys.target_namespace = self.target_namespace
       
        kf = self.field.key_type
        ks = serializer_for_field(kf)
        ks.target_namespace = self.target_namespace
        
        for p in e:
            k = p.attrib.pop(ks.name)
            d[k] = ys.from_xml(p)
        
        return d

