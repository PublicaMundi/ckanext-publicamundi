import zope.interface
import zope.schema
from zope.interface import Interface

from ckanext.publicamundi.lib import vocabularies
from ckanext.publicamundi.lib.util import check_uuid
from ckanext.publicamundi.lib.metadata import IMetadata
from ckanext.publicamundi.lib.metadata.ibase import IFieldWithContext

language_code_vocabulary = vocabularies.by_name('languages-iso-639-1').get('vocabulary')

__all__ = [
    'IFieldTranslator',
    'IKeyBasedFieldTranslator',
    'IValueBasedFieldTranslator',
    'ITranslatedField',
    'IMetadataTranslator',
    'ITranslatedMetadata',
]

class IFieldTranslator(Interface):
    '''A generic interface for field translation.
    '''
    
    def get(field, language, state='active'):
        '''Return a translated bound field for the given pair (field, language).
        
        This method should always return unicode text, or None if no translation exists.

        The `field` parameter is expected to be a bound Field, with a proper (key, value) 
        context (i.e. field.context should provide IFieldContext).
        
        The `language` parameter should be a valid language code (iso-639-1).
        '''

    def translate(field, value, language, state='active'):
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

    source_language = zope.schema.Choice(vocabulary=language_code_vocabulary, required=True)

    namespace = zope.schema.NativeStringLine(required=True)

class IValueBasedFieldTranslator(IFieldTranslator):

    text_domain = zope.schema.NativeStringLine(default=None) 

class IKeyBasedFieldTranslator(IFieldTranslator):

    package_id = zope.schema.NativeStringLine(required=True, constraint=check_uuid)

class ITranslatedField(IFieldWithContext):
    
    pass

class ITranslatedMetadata(IMetadata):

    source_language = zope.schema.Choice(vocabulary=language_code_vocabulary, required=True)
    
    language = zope.schema.Choice(vocabulary=language_code_vocabulary, required=True)
 
class IMetadataTranslator(zope.interface.Interface):

    source_language = zope.schema.Choice(vocabulary=language_code_vocabulary, required=True)

    def get(language):
        '''Fetch available translations and return an ITranslatedMetadata object.
        '''

    def get_field_translators():
        '''Get suitable translators for a metadata object.
        
        This method returns a list of field translators (providing IFieldTranslator),
        which should be tried (in this order) to manipulate translations for fields.
        '''

  
