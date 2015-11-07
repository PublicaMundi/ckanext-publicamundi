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
        Column('package', types.UnicodeText(), ForeignKey(Package.id, ondelete='cascade'), nullable=False),
        Column('source_language', Language),
        Column('language', Language, nullable=False),
        Column('key', types.UnicodeText(), nullable=False),
        Column('value', types.UnicodeText()),
        Column('state', TranslationState, default='active'),
        Index('ix_package_translation_package_key', 'package', 'key'),
        UniqueConstraint('package', 'source_language', 'language', 'key'),
    )
