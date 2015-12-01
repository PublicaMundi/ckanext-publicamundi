from sqlalchemy import Column, String

from ckanext.publicamundi.analytics.controllers.configmanager import Base


class SystemInfo(Base):
    __tablename__ = "systeminfo"
    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    LATEST_DATE_KEY = "latest_date"

    def __init__(self, key, value):
        self.key = key
        self.value = value