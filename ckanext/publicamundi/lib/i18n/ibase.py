import zope.interface
import zope.schema

from ckanext.publicamundi.lib import vocabularies
from ckanext.publicamundi.lib.util import check_uuid

class ITranslator(zope.interface.Interface):
    '''A generic interface for both key-based and term-based translation mechanisms.
    '''
    
    def get(key, language, state='active'):
        '''Return a translation for the given pair (key, language).
        
        This method should always return unicode text, or None if no translation exists.

        The key parameter can be supplied in either a serialized form (a plain string)
        or as a key path (a tuple).
        
        The language parameter should be a valid language code (iso-639-1).
        '''

    def translate(key, value, language, state='active'):
        '''Add or update translation for a given pair (key, language).
        '''

    def discard(key=None, language=None):
        '''Discard existing translations.

        If language is None, discard everything on a given key
        If key is None, discard everything (for this package) on the given language.
        
        Return number of discarded translations.
        '''

    source_language = zope.schema.Choice(
        vocabulary = vocabularies.get_by_name('languages-iso-639-1').get('vocabulary'),
        required = True)

class ITermTranslator(ITranslator):

    text_domain = zope.schema.NativeStringLine(default=None) 

class IPackageTranslator(ITranslator):

    package_id = zope.schema.NativeStringLine(required=True, constraint=check_uuid)

