import pytest
from database.db_management.models.db_connection import db_connection
import database.tests.utils.population_utils as population_utils
from database.tests.test_config import CONFIG
import database.config as config
from database.tests.utils.dbUtils import DBUtils


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


@pytest.yield_fixture(autouse=True, scope='function', name='person_data')
def populate_person_information_to_db():
    # Note this uses connection and utils from database/ project
    DBUtils.init_test_db()
    db_connection.init_database(CONFIG['test_db_name'], CONFIG['db_user'])
    db_connection.connect()
    database = db_connection.get_database()

    config.CONFIG['anonymize'] = False
    DBUtils.truncate_db()
    data = population_utils.populate_from_json(database, "./database/tests/populate/data/person2.json")
    db_connection.close()
    return data
