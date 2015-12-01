from ckanext.publicamundi.analytics.controllers.configmanager import Base, database_engine


class DbManager:
    def __init__(self):
        pass

    @staticmethod
    def create_schema():
        Base.metadata.create_all(database_engine)

    @staticmethod
    def drop_all_tables():
        Base.metadata.drop_all(database_engine)