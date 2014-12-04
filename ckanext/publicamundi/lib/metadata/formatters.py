'''Provide formatters for zope.schema fields

We provide named adapters for IFormatter interface. These adapters are named 
according to their names as "format:<name>". An unnamed adapter also exists
as "format" and stands for the default formatter.

'''

import datetime
import zope.interface
import zope.schema
from collections import namedtuple

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.util import quote, raise_for_stub_method
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.fields import (
    build_adaptee, check_multiadapter_ifaces)
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata.ibase import IFormatSpec, IFormatter

__all__ = [
    'field_format_adapter',
    'field_format_multiadapter',
    'FormatSpec',
    'BaseFormatter', 
    'formatter_for_field',
]

# Format specifiers

class FormatSpec(namedtuple('_FormatSpec', ('name', 'opts'))):
    
    zope.interface.implements(IFormatSpec)

    __slots__ = ()

    def __str__(self):
        '''Return as a format-spec string.
        '''
        
        opts_str = ','.join(
            ('%s' %(t[0]) if t[1] is True else '%s=%s' % (t) 
                for t in  self.opts.iteritems()))

        return '%s:%s' %(self.name, opts_str) if self.name else ''

    @classmethod
    def parse(cls, spec):
        '''Parse a format-spec string into a FormatSpec object.
        
        Examples:
            >>> FormatSpec.parse('default:aa,bb,cc=3,quote')
            FormatSpec(name='default', opts={'aa': True, 'cc': '3', 'bb': True, 'quote': True})

            >>> FormatSpec.parse('default')
            FormatSpec(name='default', opts={})

        '''

        t = spec.split(':')
        name, opts_str = t[0], t[1] if len(t) > 1 else None
        
        if opts_str:
            opts_iter = (t.strip().split('=') for t in opts_str.split(','))
            opts = ((t[0], t[1] if len(t) > 1 else True) for t in opts_iter)
        else:
            opts = ()
        
        return cls(name=name, opts=dict(opts))

# Decorators for adaptation

def decorator_for_multiadapter(required_ifaces, qualifier, is_fallback):
    def decorate(cls):
        adapter_names = set()
        if not qualifier or is_fallback:
            adapter_names.add('format')
        if qualifier:
            adapter_names.add('format:%s' % (qualifier))
        for name in adapter_names:
            adapter_registry.register(required_ifaces, IFormatter, name, cls)
        return cls
    return decorate   

def field_format_adapter(required_iface, name='', is_fallback=False):
    assert required_iface.isOrExtends(IField)
    return decorator_for_multiadapter([required_iface], name, is_fallback)

def field_format_multiadapter(required_ifaces, name='', is_fallback=False):
    check_multiadapter_ifaces(required_ifaces)
    return decorator_for_multiadapter(required_ifaces, name, is_fallback)   

# Utilities

def formatter_for_field(field, name=''):
    '''Get a proper formatter for a zope.schema.Field instance.
    '''  
    assert isinstance(field, zope.schema.Field)
    
    # Build adaptee vector
    
    adaptee = build_adaptee(field, expand_collection=True)

    # Lookup
    
    candidates = ['format']
    if name:
        candidates.insert(0, 'format:%s' % (name))
    
    formatter = None
    while adaptee:
        for candidate in candidates: 
            formatter = adapter_registry.queryMultiAdapter(
                adaptee, IFormatter, candidate)
            if formatter:
                break
        if formatter:
            break
        # Fallback to a more general version of this adaptee    
        adaptee.pop()

    if formatter:
        formatter.requested_name = name
    return formatter

def config_for_field(field, name=''):
    fo_tag = field.queryTaggedValue('format')
    return fo_tag.get(name) if fo_tag else None
    
# Formatters

class BaseFormatter(object):
    
    zope.interface.implements(IFormatter)
    
    def format(self, value=None, opts={}):
        return unicode(value)

class BaseFieldFormatter(BaseFormatter):
    
    def __init__(self, field, *args):
        self.field = field
        self.requested_name = None

    # Interface IFormatter
    
    def format(self, value=None, opts={}):
        if value is None:
            value = self.field.context.value
        return self._format(value, opts)
    
    # Implementation

    def _format(self, value, opts):
        raise_for_stub_method()

@field_format_adapter(IField)
class FieldFormatter(BaseFieldFormatter):
    '''A fallback formatter for any field (IField)'''

    def _format(self, value, opts):
        return unicode(value)

@field_format_adapter(IStringField)
@field_format_adapter(IStringLineField)
class StringFieldFormatter(BaseFieldFormatter):
    
    encoding = 'utf-8'

    def _format(self, value, opts):
        assert isinstance(value, str)
        s = value.decode(self.encoding)
        return quote(s) if opts.get('quote') else s

@field_format_adapter(ITextLineField)
@field_format_adapter(ITextField)
class TextFieldFormatter(BaseFieldFormatter):

    def _format(self, value, opts):
        assert isinstance(value, unicode)
        return quote(value) if opts.get('quote') else value

@field_format_adapter(IFloatField)
class FloatFieldFormatter(BaseFieldFormatter):

    precision = 4
    
    def _format(self, value, opts):
        assert isinstance(value, float)
        try:
            precision = int(opts.get('precision'))
        except:
            precision = self.precision
        return u'{0:.{1}f}'.format(value, precision)

@field_format_adapter(IPasswordField)
class PasswordFieldFormatter(BaseFieldFormatter):
    
    def _format(self, value, opts):
        return '*'

@field_format_adapter(IChoiceField)
class ChoiceFieldFormatter(BaseFieldFormatter):
    
    def _format(self, value, opts):
        assert isinstance(value, basestring)
        # If lookup fails, raise an exception
        try:
            term = self.field.vocabulary.getTerm(value)
        except:
            raise ValueError('The term "%r" does not exist' %(value))
        s = term.title
        return u'<%s>' % s if opts.get('quote') else s
        
@field_format_adapter(IDatetimeField)
@field_format_adapter(IDateField)
@field_format_adapter(ITimeField)
class DatetimeFieldFormatter(BaseFieldFormatter):

    def _format(self, value, opts):
        assert isinstance(value, (
            datetime.datetime, datetime.date, datetime.time))
        s = value.isoformat()
        return u'<%s>' % s if opts.get('quote') else s

@field_format_adapter(ITupleField)
@field_format_adapter(IListField)
class ListFieldFormatter(BaseFieldFormatter):
    
    delimiter = ', '

    def _format(self, values, opts):
        assert isinstance(values, (list, tuple))
        field, delimiter = self.field, self.delimiter

        yf = formatter_for_field(field.value_type, self.requested_name)
        assert yf, 'Cannot find a formatter for %s' %(field.value_type)
        f = lambda t: yf.format(t, opts)

        s = delimiter.join(map(f, values))
        return u'[%s]' % s if opts.get('quote') else s

@field_format_adapter(IDictField)
class DictFieldFormatter(BaseFieldFormatter):
    
    delimiter = u', '
    
    def _format(self, data, opts):
        assert isinstance(data, dict)
        field, delimiter = self.field, self.delimiter

        yf = formatter_for_field(field.value_type, self.requested_name)
        assert yf, 'Cannot find a formatter for %s' %(field.value_type)
        f = lambda t: unicode(t[0]) + ': ' + yf.format(t[1], opts)
        
        s = delimiter.join(map(f, data.iteritems()))
        return u'{%s}' % s if opts.get('quote') else s

@field_format_multiadapter([IListField, IStringLineField])
class ListOfStringFieldFormatter(ListFieldFormatter):

    encoding = 'utf-8'
    
    def _decode_value(self, v):
        return v.decode(self.encoding)

    def _format(self, values, opts):
        assert isinstance(values, (list, tuple))
        decode, delimiter = self._decode_value, self.delimiter
        s = delimiter.join(map(quote, map(decode, values)))
        return u'[%s]' % s if opts.get('quote') else s

@field_format_multiadapter([IListField, ITextLineField])
class ListOfTextFieldFormatter(ListFieldFormatter):
    
    def _format(self, values, opts):
        assert isinstance(values, (list, tuple))
        delimiter = self.delimiter
        s = delimiter.join(map(quote, values))
        return u'[%s]' % s if opts.get('quote') else s

@field_format_multiadapter([IDictField, IStringField])
class DictOfStringFieldFormatter(DictFieldFormatter):

    encoding = 'utf-8'
    
    def _decode_value(self, v):
        return v.decode(self.encoding)

    def _format(self,  data, opts):
        assert isinstance(data, dict)
        decode, delimiter = self._decode_value, self.delimiter
        f = lambda t: unicode(t[0]) + ': ' + quote(decode(t[1]))
        s = delimiter.join(map(f, data.iteritems()))
        return u'{%s}' % s if opts.get('quote') else s

@field_format_multiadapter([IDictField, ITextLineField])
class DictOfTextFieldFormatter(DictFieldFormatter):
    
    def _format(self, data, opts):
        assert isinstance(data, dict)
        delimiter = self.delimiter
        f = lambda t: unicode(t[0]) + ': ' + quote(t[1])
        s = delimiter.join(map(f, data.iteritems()))
        return u'{%s}' % s if opts.get('quote') else s

