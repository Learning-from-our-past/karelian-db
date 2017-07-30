from peewee import *
import os


class DbConnection:

    def __init__(self):
        self.database = PostgresqlDatabase(None)

    def init_database(self, db_name=os.environ['DB_NAME'], db_user=os.environ['DB_USER']):
        self.database.init(db_name, **{'user': db_user})

    def connect(self):
        self.database.connect()

    def get_database(self):
        return self.database


db_connection = DbConnection()
