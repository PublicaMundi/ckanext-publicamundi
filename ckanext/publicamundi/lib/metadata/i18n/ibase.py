import zope.interface
import zope.schema
from zope.interface import Interface

from ckanext.publicamundi.lib import vocabularies
from ckanext.publicamundi.lib.util import check_uuid
from ckanext.publicamundi.lib.metadata import IMetadata
from ckanext.publicamundi.lib.metadata.ibase import IFieldWithContext

language_vocabulary = vocabularies.by_name('languages-iso-639-1').get('vocabulary')

__all__ = [
    'IFieldTranslation',
    'IKeyBasedFieldTranslation',
    'IValueBasedFieldTranslation',
    'ITranslatedField',
    'ITranslatedMetadata',
    'ITranslator',
    'IMetadataTranslator',
]

class IFieldTranslation(Interface):
    
    def get(field, language, state='active'):
        '''Return a bound field translated for the given pair (field, language).
        
        This method should always return a bound field, or None if no translation exists.
        The  translated value (found at .context.value) should be unicode text.
        
        *Note* Maybe return just unicode text (avoid wrapping to a field) ?

        The `field` parameter is expected to be a bound field, with a proper (key, value) 
        context (i.e. field.context should provide IFieldContext).
        
        The `language` parameter should be a valid language code (iso-639-1).
        '''

    def translate(field, language, value, state='active'):
        '''Add or update translation for a given pair (field, language).

        The `field`, `language` parameters are exactly the same as in get() method.
        The `value` parameter expects the translated value for this field.
        '''

    def discard(field=None, language=None):
        '''Discard existing translations.

        The `field`, `language` parameters are exactly the same as in get() method.
        If `language` is None, discard everything on a given field
        If `field` is None, discard everything on the given language.
        
        Return number of discarded translations.
        '''

    source_language = zope.schema.Choice(vocabulary=language_vocabulary, required=True)

    namespace = zope.schema.NativeStringLine(required=True)

class IValueBasedFieldTranslation(IFieldTranslation):

    text_domain = zope.schema.NativeStringLine(default=None) 

class IKeyBasedFieldTranslation(IFieldTranslation):

    package_id = zope.schema.NativeStringLine(required=True, constraint=check_uuid)

class ITranslatedField(IFieldWithContext): pass

class ITranslatedMetadata(IMetadata):

    source_language = zope.schema.Choice(vocabulary=language_vocabulary, required=True)
    
    translation_language = zope.schema.Choice(vocabulary=language_vocabulary, required=True)
 
class ITranslator(Interface):

    def get(language):
        '''Return a translated view for given language
        '''
    
    def translate(language, translated):
        '''Translate to language, draw translations from translated.
        
        Return the translated view. 
        '''
    
    source_language = zope.schema.Choice(vocabulary=language_vocabulary, required=True)

class IMetadataTranslator(ITranslator):

    def get_field_translator(field):
        '''Get a suitable field translator for a bound field (as if this field was 
        part of a metadata object).
        
        The main use for this is to enable translation of fields not embeded in the 
        schema of a metadata object (like core metadata fields, or other top-level
        scalar fields added by 3rd-party extensions).
        '''
