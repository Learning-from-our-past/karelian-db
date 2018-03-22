import psycopg2
from psycopg2.sql import SQL as PSQL
from psycopg2.sql import Identifier
from peewee import *
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from abc import abstractmethod

"""
Provides the base class for a class that provides services to manage database during tests
such as functions to create, drop and truncate contents of the testdbs. You just subclass
this and call this base class's constructor. Pass it a config that has the following keys
with values:
    * master_db                     # e.g. postgres
    * db_admin                      # e.g. postgres
    * test_db_name                  # e.g. karelian_testdb
    * drop_database_on_init         # e.g. True
    * db_user                       # e.g. kaira
    * sql_files                     # A list of SQL files to run when initializing the database
    
The constructor also wants sequences_to_reset. This is a list of tuples, like:
    [('siirtokarjalaisten_tie', 'Person_id_seq'), ('siirtokarjalaisten_tie', 'Place_id_seq')]
These sequences get reset between tests so they do not increment to high numbers.

Finally, truncate_schema. The tables of this schema get truncated when truncate_db is called.
"""


class BaseDBUtils:
    def __init__(self, config, sequences_to_reset, truncate_schema):
        self.master_connection = psycopg2.connect(dbname=config['master_db'], user=config['db_admin'],
                                                  host='localhost')

        self.master_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.master_cursor = self.master_connection.cursor()

        self.test_db_connection = None
        self.peewee_database = PostgresqlDatabase(None)
        self._reset_values = sequences_to_reset
        self._config = config
        self._truncate_schema = truncate_schema

    def _get_test_db_connection(self):
        return psycopg2.connect(dbname=self._config['test_db_name'], user=self._config['db_admin'], host='localhost')

    def init_test_db(self):
        """
        Initialize database to fresh state at the beginning of the tests. Either drops and creates the db
        or just truncates the existing db depending on configuration.
        :return:
        """

        if self._config['drop_database_on_init']:
            self._drop_and_create()

            self.test_db_connection = self._get_test_db_connection()
            self._create_base_db_from_sql()
            # leave it up to subclasses to decide how they want to set up their schema and things
            self._create_schema()

            self.master_cursor.close()
            self.master_connection.close()
        else:
            self.test_db_connection = self._get_test_db_connection()
            self.truncate_db()  # just truncate tables. Faster, but does not modify tables

    def close_db_connections(self):
        """
        Closes database connections. Should be called after all tests have been ran.
        """
        self.test_db_connection.cursor().close()
        self.test_db_connection.close()
        self.master_cursor.close()
        self.master_connection.close()

    def _drop_and_create(self):
        """
        Drop possible existing database and recreate it.
        """
        self.master_cursor.execute(
            "SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower(%s);",
            [self._config['test_db_name']]
        )
        db_exists = self.master_cursor.fetchone()

        if db_exists:
            self.master_cursor.execute('DROP DATABASE ' + self._config['test_db_name'])
        self.master_cursor.execute('CREATE DATABASE ' + self._config['test_db_name'])

    def _create_base_db_from_sql(self):
        self.test_db_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        # Run sql setup files which set up db, schemas and users
        for path in self._config['sql_files']:
            sqlfile = open(path, 'r')
            self.test_db_connection.cursor().execute(sqlfile.read())
            sqlfile.close()

        self.peewee_database.init(self._config['test_db_name'],
                                  **{'user': self._config['db_admin']})
        self.peewee_database.connect()

    @abstractmethod
    def _create_schema(self):
        pass

    def truncate_db(self):
        """
        Empty all tables in database.
        """
        self.test_db_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = self.test_db_connection.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE tableowner = %s AND schemaname = %s;",
                       [self._config['db_admin'], self._truncate_schema])
        tables = cursor.fetchall()

        for table in tables:
            cursor.execute(
                PSQL("TRUNCATE TABLE {}.{} CASCADE;").format(Identifier(self._truncate_schema), Identifier(table[0]))
            )

        # This query was generated with:
        # https://wiki.postgresql.org/wiki/Fixing_Sequences
        # Accessed 2018-04-10 14:11 UTC
        query_fmt = "SELECT SETVAL('{schema}.\"{sequence}\"', COALESCE(MAX(\"{id_column}\"), 1)) FROM {schema}.\"{table}\"";
        # Reset sequences so that they stay mostly the same in between the tests
        for schema, sequence in self._reset_values:
            sequence_parts = sequence.split('_')
            table = sequence_parts[0]
            id_column = sequence_parts[1]
            query = query_fmt.format(schema=schema, sequence=sequence, table=table, id_column=id_column)
            self.test_db_connection.cursor().execute(query)
