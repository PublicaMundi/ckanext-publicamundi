from sqlalchemy import Table, Column
from sqlalchemy import types 
from sqlalchemy import ForeignKey, UniqueConstraint, Index

from ckan.model import Package
from ckanext.publicamundi.model import Base

from ckanext.publicamundi.lib import languages

language_codes = languages.get_all('iso-639-1').keys()
Language = types.Enum(*language_codes, name='language_code')

translation_states = ('active', 'draft', 'deleted')
TranslationState = types.Enum(*translation_states, name='translation_state')

class PackageTranslation(Base):
    __table__ = Table('package_translation', Base.metadata,
        Column('tid', types.Integer(), primary_key=True, autoincrement=True),
        Column('package_id', types.UnicodeText(), ForeignKey(Package.id, ondelete='cascade'), nullable=False),
        Column('source_language', Language),
        Column('language', Language, nullable=False),
        Column('key', types.UnicodeText(), nullable=False),
        Column('value', types.UnicodeText()),
        Column('state', TranslationState, default='active'),
        Index('ix_package_translation_package_key', 'package_id', 'key'),
        UniqueConstraint('package_id', 'source_language', 'language', 'key'),
    )

    def __init__(self, package_id=None, source_language=None, language=None, key=None, value=None, state=None):
        self.package_id = package_id
        self.source_language = source_language
        self.language = language
        self.key = key
        self.value = value
        self.state = state
        
    def __repr__(self):
        return '<PackageTranslation package=%s key=%s language=%s>' % (
            self.package_id, self.key, self.language)
        
