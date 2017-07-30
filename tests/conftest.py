import pytest

from db_management.models.db_connection import db_connection
from tests.utils.dbUtils import DBUtils


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
    db_connection.init_database()
    db_connection.connect()
    return db_connection.get_database()
