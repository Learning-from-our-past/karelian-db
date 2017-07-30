import os
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from peewee_migrate import Router
from peewee import *
from tests.test_config import CONFIG
# Do not log useless messages about migrations during test setup
import logging
from peewee_migrate import LOGGER
LOGGER.setLevel(logging.WARN)

# FIXME: Dirty way to pass the schema for migration history so that peewee_migrate will work properly.
# More information: https://github.com/klen/peewee_migrate/issues/51
from peewee_migrate import MigrateHistory
MigrateHistory._meta.schema = 'system'

"""
Provides basic services to manage database during tests such as functions to create, drop and truncate
contents of the testdbs. Loads configurations from test-config.json file on start up.
"""
class DBUtils:


    def __init__(self):
        self.master_connection = psycopg2.connect(dbname=CONFIG['master_db'], user=CONFIG['admin_user'],
                                                  host='localhost')

        self.master_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.master_cursor = self.master_connection.cursor()

        self.test_db_connection = None
        self.peewee_database = PostgresqlDatabase(None)

    def _get_test_db_connection(self):
        return psycopg2.connect(dbname=CONFIG['test_db_name'], user=CONFIG['admin_user'], host='localhost')


    def init_test_db(self):
        """
        Initialize database to fresh state at the beginning of the tests. Either drops and creates the db
        or just truncates the existing db depending on configuration.
        :return:
        """

        if CONFIG['drop_database_on_init']:
            self._drop_and_create()

            self.test_db_connection = self._get_test_db_connection()
            self._create_db_schema()

            self.master_cursor.close()
            self.master_connection.close()
        else:
            self.test_db_connection = self._get_test_db_connection()
            self.truncate_db()  # just truncate tables. Faster, but does not modify tables

    def close_db_connections(self):
        """
        Closes database connections. Should be called after all tests have been ran.
        :return:
        """
        self.test_db_connection.cursor().close()
        self.test_db_connection.close()
        self.master_cursor.close()
        self.master_connection.close()

    def _drop_and_create(self):
        """
        Drop possible existing database and recreate it.
        :return:
        """
        self.master_cursor.execute("SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower(%s);", [CONFIG['test_db_name']])
        db_exists = self.master_cursor.fetchone()

        if db_exists:
            self.master_cursor.execute('DROP DATABASE ' + CONFIG['test_db_name'])
        self.master_cursor.execute('CREATE DATABASE ' + CONFIG['test_db_name'])

    def _create_db_schema(self):
        self.test_db_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        self.test_db_connection.cursor().execute('ALTER DATABASE ' + CONFIG['test_db_name'] + ' SET search_path=extensions, public;')

        # Run sql setup file which creates db and schemas
        for path in CONFIG['sql_files']:
            sqlfile = open(path, 'r')
            self.test_db_connection.cursor().execute(sqlfile.read())
            sqlfile.close()

        self.peewee_database.init(CONFIG['test_db_name'],
                                  **{'user': os.environ['DB_USER']})
        self.peewee_database.connect()

        # Run all unapplied migrations
        router = Router(self.peewee_database)
        router.run()

    def truncate_db(self):
        """
        Empty all tables in database.
        :return:
        """
        self.test_db_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = self.test_db_connection.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE tableowner = %s AND schemaname = 'siirtokarjalaisten_tie';", [os.environ['DB_USER']])
        tables = cursor.fetchall()

        for table in tables:
            cursor.execute("TRUNCATE TABLE siirtokarjalaisten_tie." + '"' + table[0] + '"' + " CASCADE;")

DBUtils = DBUtils()
