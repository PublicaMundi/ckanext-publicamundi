'''Multilinguality API
'''

from ckanext.publicamundi.lib import languages

language_codes = languages.get_all('iso-639-1').keys()

from .ibase import *
from .package_translation import PackageTranslator
from .term_translation import TermTranslator
