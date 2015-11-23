'''Multilinguality for metadata objects
'''

from ckanext.publicamundi.lib import languages
from ckanext.publicamundi.lib.languages import check as check_language

language_codes = languages.get_all('iso-639-1').keys()

from .ibase import *
from .base import translator_for_metadata as translator_for
from .base import (translate_adapter, field_translate_adapter)
