import zope.interface
import zope.schema
from zope.interface import implements, alsoProvides
from zope.interface.verify import verifyObject

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.i18n import (
    IPackageTranslator, ITermTranslator, PackageTranslator, TermTranslator)
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import (IMetadata, Metadata)
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.base import (IFieldContext, FieldContext)

from . import language_codes
from .ibase import (ITranslatedField, ITranslatedMetadata, IMetadataTranslator)

## Decorators for adaptation

def translate_adapter(name='default'):
    def decorate(cls):
        adapter_registry.register(
            [IMetadata, None], IMetadataTranslator, 'translate:%s' % (name), cls)
        return cls
    return decorate

def field_translate_adapter(ifield, use='key'):
    assert ifield.extends(IField)
    assert use in ('key', 'value')
    itranslator = ITermTranslator if use == 'value' else IPackageTranslator
    def decorate(f):
        adapter_registry.register(
            [ifield, None, itranslator], ITranslatedField, 'translate', f)
        return f
    return decorate

## Utility

def translator_for_metadata(obj, language, name='default'):
    assert isinstance(obj, Metadata)
    translator = adapter_registry.queryMultiAdapter(
        [obj, language], IMetadataTranslator, 'translate:%s' % (name))
    return translator

def translated_field(field, language, field_translator):
    assert isinstance(field, Field)
    verifyObject(IFieldContext, field.context)
    yfield = adapter_registry.queryMultiAdapter(
        [field, language, field_translator], ITranslatedField, 'translate')
    return yfield

## Base 

@translate_adapter()
class MetadataTranslator(object):
    
    implements(IMetadataTranslator)

    def __init__(self, obj, source_language=None):
        assert isinstance(obj, Metadata)
        self.obj = obj
        self.source_language = source_language
        
    ## IMetadataTranslator interface ##

    def get(self, language):
        
        obj = self.obj
        key_prefix = getattr(obj, '__dataset_type', '')
        field_translators = self.get_translators()

        flattened = obj.to_dict(flat=True)
        for kp, value in flattened.items():
            yf = self.obj.get_field(kp)
            yf.context.key = (key_prefix,) + kp
            if yf.queryTaggedValue('translatable'):
                for translator in field_translators:
                    yf1 = translated_field(yf, language, translator)
                    if yf1:
                        flattened[kp] = yf1.context.value
                        break
        
        obj1 = type(obj)()
        obj1.from_dict(flattened, is_flat=True)
        obj1.source_language = self.source_language
        obj1.language = language

        alsoProvides(obj1, ITranslatedMetadata)
        return obj1

    def get_translators(self):
        return [
            PackageTranslator(self.obj.identifier, self.source_language),
        ]

## Translate adapters for fields 

@field_translate_adapter(ITextLineField, 'key')
@field_translate_adapter(ITextField, 'key')
def translated_text_field(field, language, translator):
    key = field.context.key
    if not field.context.value:
        return None
    translated_value = translator.get(key, language, 'active')
    if translated_value:
        return field.bind(FieldContext(key=key, value=translated_value))
    return None

@field_translate_adapter(ITextLineField, 'value')
@field_translate_adapter(ITextField, 'value')
def translated_text_field(field, language, translator):
    key = field.context.key
    value = field.context.value
    if not value:
        return None
    translated_value = translator.get(value, language, 'active')
    if translated_value:
        return field.bind(FieldContext(key=key, value=translated_value))
    return None

