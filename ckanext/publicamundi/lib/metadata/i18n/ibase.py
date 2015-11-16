import zope.interface
import zope.schema

from ckanext.publicamundi.lib import vocabularies
from ckanext.publicamundi.lib.i18n import IPackageTranslator, ITermTranslator
from ckanext.publicamundi.lib.metadata import IMetadata
from ckanext.publicamundi.lib.metadata.ibase import IFieldWithContext

language_code_vocabulary = vocabularies.by_name('languages-iso-639-1').get('vocabulary')

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

    def get_translators():
        '''Get suitable translators for a metadata object.
        
        Return a list of translator objects; each one should provide one of the following:
          * IPackageTranslator: Use package-scoped, key-based translations
          * ITermTranslator: Use domain-scoped, term-based translations 
        '''

  
