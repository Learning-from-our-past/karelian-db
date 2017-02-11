import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class DBUtils:
    _DROP_ALWAYS = False

    def __init__(self):
        self.master_connection = psycopg2.connect(dbname='postgres', user=os.environ['DB_USER'], host='localhost',
                                             password=os.environ['DB_PASSWORD'])
        self.master_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.master_cursor = self.master_connection.cursor()

        self.test_connection = None

    def _get_test_connection(self):
        return psycopg2.connect(dbname='testdb', user=os.environ['DB_USER'], host='localhost',
                                                password=os.environ['DB_PASSWORD'])

    def create_test_db(self):
        if self._DROP_ALWAYS:
            self._drop_and_create()

            self.test_connection = self._get_test_connection()
            self.create_db_schema()

            self.master_cursor.close()
            self.master_connection.close()
        else:
            self.test_connection = self._get_test_connection()
            self.truncate_db()  # just truncate tables. Faster, but does not modify tables

    def close_db_connections(self):
        self.test_connection.cursor().close()
        self.test_connection.close()
        self.master_cursor.close()
        self.master_connection.close()

    def drop_and_create(self):
        self.master_cursor.execute("SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower('testdb');")
        db_exists = self.master_cursor.fetchone()

        if db_exists:
            self.master_cursor.execute('DROP DATABASE testdb')
        self.master_cursor.execute('CREATE DATABASE testdb')

    def create_db_schema(self):
        self.test_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        sql_file_paths = ['./sql/create_db_schema.sql', './sql/create_functions.sql', './sql/create_views.sql']
        for path in sql_file_paths:
            sqlfile = open(path, 'r')
            self.test_connection.cursor().execute(sqlfile.read())
            sqlfile.close()

    def truncate_db(self):
        self.test_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = self.test_connection.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE tableowner = %s AND schemaname = 'siirtokarjalaisten_tie';", [os.environ['DB_USER']])
        tables = cursor.fetchall()

        for table in tables:
            cursor.execute("TRUNCATE TABLE siirtokarjalaisten_tie." + table[0] + " CASCADE;")

DBUtils = DBUtils()