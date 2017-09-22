from peewee import *


class DbConnection:

    def __init__(self):
        self.database = PostgresqlDatabase(None)
        self._initialized = False

    def init_database(self, db_name, db_user, password=None, host='localhost', port=5432):
        # FIXME: This is kinda funny. Check the kairatools conftest for more information
        if not self._initialized:
            user_info = {'user': db_user, 'host': host, 'port': port}

            if password:
                user_info['password'] = password

            self.database.init(db_name, **user_info)
            self._initialized = True

    def connect(self):
        self.database.connect()

    def close(self):
        self.database.close()

    def get_database(self):
        return self.database


db_connection = DbConnection()
