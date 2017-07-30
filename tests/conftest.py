import pytest

from db_management.models.db_connection import db_connection
from db_management.models.db_connection import DbConnection
from tests.utils.dbUtils import DBUtils
from tests.test_config import CONFIG


def pytest_collection_modifyitems(session, config, items):
    """
    Called after collection has been performed, may filter or re-order
    the items in-place. Use with decorator:
    @pytest.mark.only
    """
    found_only_marker = False
    for item in items.copy():
        if item.get_marker('only'):
            if not found_only_marker:
                items.clear()
                found_only_marker = True
            items.append(item)


@pytest.fixture(scope="session", autouse=True)
def database():
    DBUtils.init_test_db()
    db_connection.init_database(CONFIG['test_db_name'], CONFIG['db_user'])
    db_connection.connect()
    return db_connection.get_database()

@pytest.yield_fixture(autouse=True, scope='session', name='researcher_connection')
def researcher_db_connection():
    """
    Use this fixture with Peewee's Using() context manager to make db operations with researcher
    user instead of kaira user.
    :return:
    """
    db_connection = DbConnection()
    db_connection.init_database('karelian_testdb', 'john', '1234')
    db_connection.connect()

    yield db_connection.get_database()

    db_connection.close()