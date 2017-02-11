import unittest
import os
from tests.utils.dbUtils import DBUtils


class TestDB(unittest.TestCase):
    def setUp(self):
        DBUtils.create_test_db(False)
        pass

    def test_foo(self):
        print('foo')

    def tearDown(self):
        pass
        DBUtils.close_db_connections()