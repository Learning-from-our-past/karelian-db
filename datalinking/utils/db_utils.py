import db_management.siirtokarjalaistentie_models as db_siirtokarjalaistentie_models
import datalinking.models.katiha_models as db_katiha_models
from db_management.database_config import CONFIG
from db_management.db_connection import DbConnection


"""
A small utility to help connect to the DB during datalinking. Use as a context manager.
"""


class DbConnectionUtil:
    def __init__(self, db):
        db = db.casefold()
        if db == 'katiha':
            db_name = 'katiha'
            db_type = 'mysql'
            db_port = 3306
            models = db_katiha_models
        else:
            db_name = CONFIG['db_name']
            db_type = 'postgres'
            db_port = CONFIG['db_port']
            models = db_siirtokarjalaistentie_models
        self._models = models
        self._db_connection = DbConnection(db_type=db_type)
        self._db_connection.init_database(db_name=db_name, db_user=CONFIG['db_user'],
                                          host='localhost', port=db_port)
        self._database = None

    def __enter__(self):
        self._db_connection.connect()
        self._database = self._db_connection.get_database()
        self._models.set_database_to_models(self._database)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._database.close()
