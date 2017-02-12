from peewee import *
import os


class DbConnection:

    def __init__(self):
        self.database = PostgresqlDatabase(None)

    def init_database(self, db_name=os.environ['DB_NAME'], db_user=os.environ['DB_USER'], db_password=os.environ['DB_PASSWORD']):
        self.database.init(db_name, **{'password': db_password, 'user': db_user})

    def connect(self):
        self.database.connect()

    def get_database(self):
        return self.database


db_connection = DbConnection()
