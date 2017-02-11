import unittest
from tests.utils.dbUtils import DBUtils
from models.db_connection import db_connection


class TestDB(unittest.TestCase):
    def setUp(self):
        DBUtils.init_test_db()
        db_connection.init_database()
        db_connection.connect()

    def test_foo(self):
        print('foo')

    def tearDown(self):
        DBUtils.close_db_connections()
