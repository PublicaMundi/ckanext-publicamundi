import zope.interface
import zope.schema
from zope.interface import implements, alsoProvides
from zope.interface.verify import verifyObject

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import (IMetadata, Metadata)
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.base import (IFieldContext, FieldContext)

from .ibase import (
    IFieldTranslator, IValueBasedFieldTranslator, IKeyBasedFieldTranslator)
from .ibase import (
    ITranslatedField, ITranslatedMetadata, IMetadataTranslator)
from . import package_translation
from . import term_translation

## Decorators for adaptation

def translate_adapter(name='default'):
    def decorate(cls):
        adapter_registry.register(
            [IMetadata, None], IMetadataTranslator, 'translate:%s' % (name), cls)
        return cls
    return decorate

def field_translate_adapter(ifield, use='key'):
    assert ifield.extends(IField)
    assert use in {'key', 'value'}

    itranslator = IKeyBasedFieldTranslator
    if use == 'value':
        itranslator = IValueBasedFieldTranslator
     
    def decorate(factory):
        adapter_registry.register(
            [ifield, None, itranslator], ITranslatedField, 'translate', factory)
        return factory
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
    if yfield:
        # If adapted, declare that directly provides ITranslatedField
        alsoProvides(yfield, ITranslatedField)
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
        
        key_prefix = getattr(self.obj, '__dataset_type', '')
        field_translators = self.get_field_translators()

        # Find all available translations 

        flattened = self.obj.to_dict(flat=True)
        for kp, value in flattened.items():
            yf = self.obj.get_field(kp)
            yf.context.key = (key_prefix,) + kp
            if yf.queryTaggedValue('translatable'):
                for translator in field_translators:
                    yf1 = translated_field(yf, language, translator)
                    if yf1:
                        flattened[kp] = yf1.context.value
                        break
        
        # Build a translated object

        obj = type(self.obj)()
        obj.from_dict(flattened, is_flat=True)
        obj.source_language = self.source_language
        obj.language = language

        alsoProvides(obj, ITranslatedMetadata)
        return obj

    def get_field_translators(self):
        return [
            package_translation.FieldTranslator(
                self.obj.identifier, self.source_language),
        ]

## Register translate adapters for fields

@field_translate_adapter(ITextLineField, 'key')
@field_translate_adapter(ITextField, 'key')
def translated_text_field(field, language, translator):
    return translator.get(field, language)

@field_translate_adapter(ITextLineField, 'value')
@field_translate_adapter(ITextField, 'value')
def translated_text_field(field, language, translator):
    return translator.get(field, language)
   
