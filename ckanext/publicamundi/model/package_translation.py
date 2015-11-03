from sqlalchemy import Table, Column
from sqlalchemy import types 
from sqlalchemy import ForeignKey, UniqueConstraint, Index

from ckan.model import Package
from ckanext.publicamundi.model import Base

from ckanext.publicamundi.lib import languages

language_codes = languages.get_all('iso-639-1').keys()
language_type = types.Enum(*language_codes, name='language_code')

state_type = types.Enum('active', 'draft', 'deleted', name='translation_state')

class PackageTranslation(Base):
    __tablename__ = 'package_translation'

    tid = Column('tid', types.Integer(), primary_key=True, autoincrement=True)
    package_id = Column('package_id', types.UnicodeText(), ForeignKey(Package.id), nullable=False)
    source_language = Column('source_language', language_type)
    target_language = Column('target_language', language_type, nullable=False)
    key = Column('key', types.UnicodeText(), nullable=False)
    value = Column('value', types.UnicodeText())
    state = Column('state', state_type, default='active')
    
    ix1 = Index('ix_package_translation_package_id', 'package_id')
    uq1 = UniqueConstraint('package_id', 'source_language', 'target_language', 'key')
    
