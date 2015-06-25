import random
import datetime
import isodate
import re
import inflection
import zope.interface
import zope.schema
import zope.schema.interfaces
from lxml import etree
from lxml.etree import (Element, SubElement, ElementTree, QName)

from ckanext.publicamundi.lib.util import raise_for_stub_method
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.ibase import IXmlSerializer, IObject
from ckanext.publicamundi.lib.metadata.base import Object, FieldContext



__all__ = [
    'field_xml_serialize_adapter',
    'object_xml_serialize_adapter',
    'xml_serializer_for_field',
    'xml_serializer_factory_for_field',
    'xml_serializer_for_object', 
    'xml_serializer_factory_for_object',
]

# Decorators for adaptation

def field_xml_serialize_adapter(required_iface):
    assert required_iface.extends(IField)
    def decorate(cls):
        adapter_registry.register(
            [required_iface], IXmlSerializer, 'serialize-xml', cls)
        return cls
    return decorate

def object_xml_serialize_adapter(required_iface):
    assert required_iface.isOrExtends(IObject)
    def decorate(cls):
        adapter_registry.register(
            [required_iface], IXmlSerializer, 'serialize-xml', cls)
        return cls
    return decorate

# Utilities

def serializer_for_field(field):
    '''Get an XML serializer for a zope.schema.Field instance.
    ''' 
    assert isinstance(field, zope.schema.Field)
    serializer = adapter_registry.queryMultiAdapter(
        [field], IXmlSerializer, 'serialize-xml')
    return serializer

def serializer_for_object(obj):
    '''Get an XML serializer for an IObject object.
    ''' 
    assert IObject.providedBy(obj)
    serializer = adapter_registry.queryMultiAdapter(
        [obj], IXmlSerializer, 'serialize-xml')
    return serializer

def serializer_factory_for_field(field_iface):
    '''Get an XML serializer factory for a zope.schema.Field interface.
    ''' 
    assert field_iface.extends(IField)
    factory = adapter_registry.lookup(
        [field_iface], IXmlSerializer, 'serialize-xml')
    return factory

def serializer_factory_for_object(obj_iface):
    '''Get an XML serializer factory for an IObject-based interface.
    ''' 
    assert obj_iface.isOrExtends(IObject)
    factory = adapter_registry.lookup(
        [obj_iface], IXmlSerializer, 'serialize-xml')
    return factory

xml_serializer_for_field = serializer_for_field

xml_serializer_factory_for_field = serializer_factory_for_field

xml_serializer_for_object = serializer_for_object

xml_serializer_factory_for_object = serializer_factory_for_object

# Serializers

class BaseSerializer(object):
    
    zope.interface.implements(IXmlSerializer)
   
    max_occurs = 1

    min_occurs = 1

    nsmap = { 
        'xs': 'http://www.w3.org/2001/XMLSchema'
    }

    # Interface IXmlSerializer

    target_namespace = None
    
    typename = None
    
    name = None

    def to_xsd(self, wrap_into_schema=False, type_prefix='', annotate=False):
        xsd_uri = self.nsmap['xs']
        
        # Create an xs:element element
        
        attrib = { 'name': self.name }
        
        if not wrap_into_schema:
            # If not at root, assign occurence indicators
            attrib.update({    
                'minOccurs': str(self.min_occurs),
                'maxOccurs': str(self.max_occurs),
            })

        e = Element(QName(xsd_uri, 'element'), attrib=attrib)
        
        # Append type definition
        
        e1, e1_tdefs = self._to_xsd_type(type_prefix)
        if isinstance(e1, basestring):
            e.attrib['type'] = str(e1)
        else:
            e.append(e1)
        
        # Decide what to return depending on wrap_into_schema flag
        
        if wrap_into_schema:
            root = self._root_xsd_element()
            for tdef in e1_tdefs.itervalues():
                root.append(tdef)
            root.append(e)
            return root
        else:
            return (e, e1_tdefs)
    
    def to_xml(self, o=None, nsmap=None):
        e = Element(QName(self.target_namespace, self.name), nsmap=nsmap)
        self._to_xml(o, e)
        return e
    
    def from_xml(self, e):
        qname = QName(e.tag)
        assert qname.localname == self.name and qname.namespace == self.target_namespace
        o = self._from_xml(e)
        return o
       
    def dumps(self, o=None):
        e = self.to_xml(o, nsmap={ None: self.target_namespace })
        s = etree.tostring(e, pretty_print=True, xml_declaration=True, encoding='utf-8')
        return s

    def loads(self, s):
        parser = etree.XMLParser(resolve_entities=False)
        e = etree.fromstring(s, parser)
        o = self.from_xml(e)
        return o
    
    # Implementation
    
    def _to_xsd_type(self, type_prefix):
        '''Build an XML tree representing the XSD type definition for 
        this adaptee (e.g. an xs:complexType or an xs:simpleType).
        
        This method returns a tuple of (<typ>, <tdefs>), where:
            - <tdefs>: is a mapping of type definitions, to be placed to the 
              global scope (global types).
            - <typ>: is one o the following 
                * an XSD local type definition (e.g. an xs:complexType or
                  an xs:simpleType element), as an non-empty etree element.
                * a type-name for a type, as a string.

        '''
        raise_for_stub_method()
    
    def _to_xml(self, o, e):
        '''Build the XML subtree under element e to serialize object o.
        '''
        raise_for_stub_method()

    def _from_xml(self, e):
        '''Build and return an object from XML subtree under element e. 
        '''
        raise_for_stub_method()
    
    def _root_xsd_element(self):
        '''Create and return an (empty) xs:schema element
        '''
        xsd_uri = self.nsmap['xs']
        e = Element(
            QName(xsd_uri, 'schema'), 
            nsmap = { 
                'target': self.target_namespace,    
            }, 
            attrib = {
                'targetNamespace': self.target_namespace,
                'elementFormDefault': 'qualified',
            }
        )
        return e

class BaseFieldSerializer(BaseSerializer):
    
    def __init__(self, field):
        self.field = field
        
        # Try to name this XSD type

        # Note: should we use field.context.key ?
        # The problem is that when dealing with List/Dict fields, the value_type
        # field also inherits the parent's context

        name = field.getName() or str(inflection.parameterize(field.title))
        if not name:
            try:
                name = field.getTaggedValue('name')
            except KeyError:
                pass
        
        assert name, 'The field should be named'
        
        name = inflection.underscore(name)
        self.typename = inflection.camelize(name)
        self.name = inflection.dasherize(name)
            
        # Compute occurence indicators

        self.min_occurs = 1 if field.required else 0
        self.max_occurs = 1
    
    def to_xsd(self, wrap_into_schema=False, type_prefix='', annotate=False):
        xsd_uri = self.nsmap['xs']
        
        # Create an xs:element element
        
        attrib = { 'name': self.name }    
        
        if not wrap_into_schema:
            # If not at root, assign occurence indicators
            attrib.update({    
                'minOccurs': str(self.min_occurs),
                'maxOccurs': str(self.max_occurs),
            })

        e = Element(QName(xsd_uri, 'element'), attrib=attrib)
        
        # Annotate with existing documentation

        if annotate:
            if self.field.title or self.field.description:
                e1 = SubElement(e, QName(xsd_uri, 'annotation'))
                if self.field.title:
                    e11 = SubElement(e1, QName(xsd_uri, 'appinfo'))
                    e11.text = self.field.title
                if self.field.description:
                    e12 = SubElement(e1, QName(xsd_uri, 'documentation'))
                    e12.text = self.field.description

        # Append type definition

        e2, e2_tdefs = self._to_xsd_type(type_prefix)
        if isinstance(e2, basestring):
            e.attrib['type'] = str(e2)
        else:
            e.append(e2)
        
        # Decide what to return depending on wrap_into_schema flag
        
        if wrap_into_schema:
            root = self._root_xsd_element()
            for tdef in e2_tdefs.itervalues():
                root.append(tdef)
            root.append(e)
            return root
        else:
            return (e, e2_tdefs)
    
    def to_xml(self, o=None, nsmap=None):
        e = Element(QName(self.target_namespace, self.name), nsmap=nsmap)
        if o is None:
            o = self.field.context.value
        self._to_xml(o, e)
        return e

class BaseObjectSerializer(BaseSerializer):
    
    def __init__(self, obj):
        self.obj = obj
        
        # Try to name this XSD type
        
        name = str(inflection.underscore(type(obj).__name__))
        self.typename = inflection.camelize(name)
        self.name = name = inflection.dasherize(name)
    
    def to_xml(self, o=None, nsmap=None):
        e = Element(QName(self.target_namespace, self.name), nsmap=nsmap)
        if o is None:
            o = self.obj
        self._to_xml(o, e)
        return e

@field_xml_serialize_adapter(INativeStringField)
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

        return (e, {})

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

@field_xml_serialize_adapter(IChoiceField)
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
        
        return (e, {})
  
@field_xml_serialize_adapter(ITextField)
@field_xml_serialize_adapter(ITextLineField)
class UnicodeFieldSerializer(StringFieldSerializer):

    def _to_xml(self, u, e):
        assert isinstance(u, unicode)
        e.text = u

    def _from_xml(self, e):
        return unicode(e.text)

@field_xml_serialize_adapter(IURIField)
class UriFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
        xsd_uri = self.nsmap['xs']
        
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:anyURI'
        })

        return (e, {})

    def _to_xml(self, s, e):
        assert isinstance(s, str)
        e.text = s

    def _from_xml(self, e):
        return str(e.text)

@field_xml_serialize_adapter(IIntField)
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
       
        return (e, {})
    
    def _to_xml(self, n, e):
        assert isinstance(n, int)
        e.text = str(n)

    def _from_xml(self, e):
        return int(e.text)

@field_xml_serialize_adapter(IBoolField)
class BoolFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:simpleType element

        e = Element(QName(xsd_uri, 'simpleType'))
        e1 = SubElement(e, QName(xsd_uri, 'restriction'), attrib={
            'base': 'xs:boolean'
        })

        return (e, {})
    
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

@field_xml_serialize_adapter(IFloatField)
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

        return (e, {})
   
    def _to_xml(self, n, e):
        assert isinstance(n, float)
        e.text = str(n)

    def _from_xml(self, e):
        return float(e.text)

@field_xml_serialize_adapter(IDatetimeField)
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

        return (e, {})

    def _to_xml(self, t, e):
        assert isinstance(t, datetime.datetime)
        e.text = t.isoformat()

    def _from_xml(self, e):
        s = str(e.text)
        d = isodate.parse_datetime(s)
        return d

@field_xml_serialize_adapter(IDateField)
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

        return (e, {})
    
    def _to_xml(self, t, e):
        assert isinstance(t, datetime.date)
        e.text = t.isoformat()

    def _from_xml(self, e):
        s = str(e.text)
        d = isodate.parse_date(s)
        return d

@field_xml_serialize_adapter(ITimeField)
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

        return (e, {})
    
    def _to_xml(self, t, e):
        assert isinstance(t, datetime.time)
        e.text = t.isoformat()
    
    def _from_xml(self, e):
        s = str(e.text)
        t = isodate.parse_time(s)
        return t

@field_xml_serialize_adapter(IListField)
class ListFieldSerializer(BaseFieldSerializer):

    def _to_xsd_type(self, type_prefix):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:complexType element

        e = Element(QName(xsd_uri, 'complexType'))
        e1 = SubElement(e, QName(xsd_uri, 'sequence'))
        
        yf = self.field.value_type

        ys = serializer_for_field(yf)
        ys.target_namespace = self.target_namespace

        ys_prefix = '_'.join((type_prefix, self.typename, 'Y'))
        ye, ye_tdefs = ys.to_xsd(type_prefix=ys_prefix)
        
        ye.attrib.update({ 
            'maxOccurs': str(self.field.max_length or 'unbounded'),
            'minOccurs': str(self.field.min_length or 0),
        })
        e1.append(ye)
      
        return (e, ye_tdefs)
    
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

@field_xml_serialize_adapter(IDictField)
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

        ys_prefix = '_'.join((type_prefix, self.typename, 'Y'))
        ye, ye_tdefs = ys.to_xsd(type_prefix=ys_prefix)    
        
        ye.attrib['maxOccurs'] = 'unbounded'
        e1.append(ye)

        # Extend type for item's element (ye) to carry a "key" attribute
        
        tdefs = ye_tdefs
        
        kf = self.field.key_type
        ks = serializer_for_field(kf)
        ks.target_namespace = self.target_namespace
        
        ks_prefix = '_'.join((type_prefix, self.typename, 'K'))
        ke, ke_tdefs = ks.to_xsd(type_prefix=ks_prefix)
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
            yt_tname = '_'.join((ys_prefix, ys.typename))
            yt.attrib['name'] = yt_tname
            # Move original xs:simpleType definition to the global scope
            ye.remove(yt)
            tdefs[yt_tname] = yt
            # Define a new xs:complexType based on yt type definition
            ye1 = SubElement(ye, xs('complexType'))
            ye11 = SubElement(ye1, xs('simpleContent'))
            ye111 = SubElement(ye11, xs('extension'), attrib={
                'base': 'target:' + yt_tname, 
            })
            ye111.append(ae)
        else:
            # Handle an xs:complexType definition
            yt.append(ae)

        return (e, tdefs)
    
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

@field_xml_serialize_adapter(IObjectField)
class ObjectFieldSerializer(BaseFieldSerializer):
    
    def _to_xsd_type(self, type_prefix):
        xsd_uri = self.nsmap['xs']
        f = self.field

        obj = None
        if f.context and isinstance(f.context.value, Object):
            obj = f.context.value
        else:
            obj = Object.Factory(f.schema)()

        # Create an xs:complexType element
        
        e = Element(QName(xsd_uri, 'complexType'))
        e1 = SubElement(e, QName(xsd_uri, 'sequence'))
        
        # Append the XSD definition for obj-typed objects

        ys = serializer_for_object(obj)
        ys.target_namespace = self.target_namespace
        
        ye, ye_tdefs = ys.to_xsd(type_prefix=type_prefix)
        e1.append(ye)

        return (e, ye_tdefs)

    def _to_xml(self, o, e):
        
        ys = serializer_for_object(o)
        ys.target_namespace = self.target_namespace
        
        e.append(ys.to_xml(o))

    def _from_xml(self, e):
        f = self.field

        obj = None
        if f.context and isinstance(f.context.value, Object):
            obj = f.context.value
        else:
            obj = Object.Factory(f.schema)()
        
        ys = serializer_for_object(obj)
        ys.target_namespace = self.target_namespace

        p = e[0]
        
        o = ys.from_xml(p)
        return o

@object_xml_serialize_adapter(IObject)
class ObjectSerializer(BaseObjectSerializer):
    '''Provide an XML serializer for derivatives of Object
    '''

    def _to_xsd_type(self, type_prefix):
        xsd_uri = self.nsmap['xs']
         
        # Create an xs:complexType element

        # Note: This type-name will not be prefixed with type_prefix, as it is
        # computed from the object's type-name (and we want to re-use it).
        
        tname = self.typename
        e = Element(QName(xsd_uri, 'complexType'), attrib={ 'name': tname })
        e1 = SubElement(e, QName(xsd_uri, 'all'))
        
        # Create an xs:element for each field
        
        ys_prefix = type_prefix + '_' + self.typename
        tdefs = {}
        for k, yf in self.obj.iter_fields(exclude_properties=True):
            yv = yf.get(self.obj)
            yf1 = yf.bind(FieldContext(key=k, value=yv))
            ys = serializer_for_field(yf1)
            ys.target_namespace = self.target_namespace
            ye, ye_tdefs = ys.to_xsd(type_prefix=ys_prefix)
            e1.append(ye)
            tdefs.update(ye_tdefs)
        
        tdefs[tname] = e
        return ('target:' + tname, tdefs)
    
    def _to_xml(self, obj, e):
        assert isinstance(obj, type(self.obj))

        for k, yf in obj.iter_fields(exclude_properties=True):
            yv = yf.get(obj)
            if yv is None:
                continue
            yf1 = yf.bind(FieldContext(key=k, value=yv))
            ys = serializer_for_field(yf1)
            ys.target_namespace = self.target_namespace
            e.append(ys.to_xml(yv)) 

    def _from_xml(self, e):
        schema = self.obj.get_schema()
        factory = type(self.obj)
        obj = factory()
        
        # Fixme: Why dont we directly update self.obj?

        for p in e:
            k = QName(p.tag).localname
            k = inflection.underscore(k)
            yf = schema.get(k)
            assert yf, 'Expected a field named %s at schema %s' %(k, schema)
            yf1 = yf.bind(FieldContext(key=k, value=yf.get(self.obj)))
            ys = serializer_for_field(yf1)
            ys.target_namespace = self.target_namespace
            yf.set(obj, ys.from_xml(p))
        
        return obj

