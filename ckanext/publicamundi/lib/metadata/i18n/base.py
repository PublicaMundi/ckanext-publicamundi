import zope.interface
import zope.schema
from zope.interface import implementer, alsoProvides
from zope.interface.verify import verifyObject

from ckanext.publicamundi.lib import logger
from ckanext.publicamundi.lib.languages import (ILanguage, Language)
from ckanext.publicamundi.lib.metadata import adapter_registry
from ckanext.publicamundi.lib.metadata import (IMetadata, Metadata)
from ckanext.publicamundi.lib.metadata.fields import *
from ckanext.publicamundi.lib.metadata.base import (IFieldContext, FieldContext)

from .ibase import (
    IFieldTranslation, IValueBasedFieldTranslation, IKeyBasedFieldTranslation)
from .ibase import (
    ITranslatedField, ITranslatedMetadata, ITranslator, IMetadataTranslator)
from . import package_translation
from . import term_translation

## Decorators for adaptation

def translate_adapter(name='default'):
    name = 'translate:%s' % (name)
    def decorate(cls):
        adapter_registry.register(
            [IMetadata, ILanguage], IMetadataTranslator, name, cls)
        return cls
    return decorate

def field_translate_adapter(ifield, use='key'):
    assert ifield.extends(IField)
    assert use in {'key', 'value'}
    
    itranslation = IKeyBasedFieldTranslation
    if use == 'value':
        itranslation = IValueBasedFieldTranslation
     
    name = 'translate'
    def decorate(cls):
        adapter_registry.register(
            [ifield, ILanguage, itranslation], ITranslator, name, cls)
        return cls
    return decorate

## Utility

def translator_for_metadata(md, source_language, name='default'):
    assert isinstance(md, Metadata)
    name = 'translate:%s' % (name)
    translator = adapter_registry.queryMultiAdapter(
        [md, Language(source_language)], IMetadataTranslator, name)
    return translator

def translator_for_field(field, source_language, field_translation):
    assert isinstance(field, Field)
    verifyObject(IFieldContext, field.context)
    
    if source_language != field_translation.source_language:
        raise ValueError(
            'The field translation is built for a different source language')
    
    name = 'translate'
    translator = adapter_registry.queryMultiAdapter(
        [field, Language(source_language), field_translation], ITranslator, name)
    return translator

## Base 

@translate_adapter()
@implementer(IMetadataTranslator)
class MetadataTranslator(object):
    
    def __init__(self, md, source_language=None):
        assert isinstance(md, Metadata)
        self.md = md
        self.source_language = source_language.code
        self._setup_field_translation()
        
    def _setup_field_translation(self):
        '''Setup a tuple of (available) field translations.

        This tuple must contain objects providing IFieldTranslation, and it will
        be visited (in order) to manipulate translations for actual fields.

        Override to provide alternative translation mechanisms.
        '''

        self._translations = (
            package_translation.FieldTranslation(
                self.md.identifier, self.source_language),
        )
    
    def _make_metadata_from_dict(self, d):
        '''Load a metadata object from a dict.
        '''
    
        load_opts = {
            'unserialize-keys': False,
            'unserialize-values': 'default'
        }
        md = type(self.md)()
        md.from_dict(d, is_flat=False, opts=load_opts)
        
        return md
    
    ## ITranslator interface ##

    def translate(self, language, translated):

        source_language = self.source_language
        key_prefix = getattr(self.md, '_dataset_type_', '')
        
        # Draw translations from `translated`
        
        if isinstance(translated, dict):
            translated = self._make_metadata_from_dict(translated)
        assert isinstance(translated, type(self.md)), \
            'Expected an instance of %s' % (type(self.md))

        # Note: The following will only add/update translations for fields that are
        # present in the source metadata object (i.e. self.md).

        flattened = self.md.to_dict(flat=True)
        for kp, value in flattened.items():
            yf = self.md.get_field(kp)
            yf.context.key = (key_prefix,) + kp
            if yf.queryTaggedValue('translatable'):
                try:
                    yf1 = translated.get_field(kp)
                except Exception as ex:
                    yf1 = None
                if not (yf1 and yf1.context.value):
                    continue # no translation for kp
                for translation in self._translations:
                    tr = translator_for_field(yf, source_language, translation)
                    if not tr:
                        continue # no registered translator
                    yf1 = tr.translate(language, yf1.context.value)
                    flattened[kp] = yf1.context.value
                    break # translated field
        
        # Build and return a metadata object

        md = type(self.md)()
        md.from_dict(flattened, is_flat=True)
        md.source_language = self.source_language
        md.translation_language = language

        return md
        
    def get(self, language):
        
        source_language = self.source_language
        key_prefix = getattr(self.md, '_dataset_type_', '')

        # Lookup all available translations 
        
        flattened = self.md.to_dict(flat=True)
        for kp, value in flattened.items():
            yf = self.md.get_field(kp)
            yf.context.key = (key_prefix,) + kp
            if yf.queryTaggedValue('translatable'):
                for translation in self._translations:
                    tr = translator_for_field(yf, source_language, translation)
                    if not tr:
                        continue # no registered translator
                    yf1 = tr.get(language)
                    if yf1:
                        flattened[kp] = yf1.context.value
                        break # translated field
        
        # Build a translated metadata object

        md = type(self.md)()
        md.from_dict(flattened, is_flat=True)
        md.source_language = self.source_language
        md.translation_language = language

        alsoProvides(md, ITranslatedMetadata)
        return md

    ## IMetadataTranslator interface ##

    def get_field_translator(self, yfield):
        source_language = self.source_language
        tr = None
        for translation in self._translations:
            tr = translator_for_field(yfield, source_language, translation)
            if tr:
                break
        return tr

## Register translate adapters for fields

class DefaultFieldTranslator(object):
    '''The default field translator: just invoke the given field-level translation
    mechanism on given (bound) fields.
    '''

    def __init__(self, field, source_language, translation):
        self.field = field
        self.source_language = source_language.code
        self.translation = translation
    
    def get(self, language):
        return self.translation.get(self.field, language)

    def translate(self, language, translated):
        return self.translation.translate(self.field, language, translated)

@field_translate_adapter(ITextLineField, 'key')
@field_translate_adapter(ITextField, 'key')
class _TextFieldTranslator(DefaultFieldTranslator): pass

@field_translate_adapter(ITextLineField, 'value')
@field_translate_adapter(ITextField, 'value')
class _TextFieldTranslator(DefaultFieldTranslator): pass
   
