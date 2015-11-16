'''Multilinguality for metadata objects
'''

from ckanext.publicamundi.lib import languages

language_codes = languages.get_all('iso-639-1').keys()

from .base import translator_for_metadata as translator_for
