from peewee import *


class DbConnection:

    def __init__(self, db_type='postgres'):
        db_type = db_type.casefold()
        if db_type.casefold() == 'postgres':
            self.database = PostgresqlDatabase(None)
        elif db_type.casefold() == 'mysql':
            self.database = MySQLDatabase(None)
        else:
            raise Exception('Unrecognized database type! Try one of [\'postgres\', \'mysql\']')

    def init_database(self, db_name, db_user, password=None, host='localhost', port=5432):
        user_info = {'user': db_user, 'host': host, 'port': port}

        if password:
            user_info['password'] = password

        self.database.init(db_name, **user_info)

    def connect(self):
        self.database.connect()

    def close(self):
        self.database.close()

    def get_database(self):
        return self.database


db_connection = DbConnection()
