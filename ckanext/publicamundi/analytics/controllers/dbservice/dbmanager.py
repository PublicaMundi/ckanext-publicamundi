from ckanext.publicamundi.analytics.controllers import configmanager

class DbManager:
    def __init__(self):
        pass

    @staticmethod
    def create_schema():
        Base = configmanager.Base
        engine = configmanager.database_engine
        Base.metadata.create_all(engine)

    @staticmethod
    def drop_all_tables():
        Base = configmanager.Base
        engine = configmanager.database_engine
        Base.metadata.drop_all(engine)
