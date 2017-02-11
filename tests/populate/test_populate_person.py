import pytest

class TestClass:


    def test_foo(self, database):
        print('foo', type(database))

    def test_bar(self, database):
        print('bar', type(database))
