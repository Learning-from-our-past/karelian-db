import unittest
import os
from tests.utils.dbUtils import DBUtils


class TestDB(unittest.TestCase):
    def setUp(self):
        DBUtils.init_test_db()
        pass

    def test_foo(self):
        print('foo')

    def tearDown(self):
        pass
        DBUtils.close_db_connections()