import pytest

import common.database_config as config
import common.siirtokarjalaistentie_models as db_siirtokarjalaistentie_models
import common.testing.population_utils as population_utils
from common.db_connection import DbConnection
from common.db_connection import db_connection
from common.testing.database_test_config import CONFIG
from common.testing.dbUtils import DBUtils
from db_management.update_report import update_report


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


@pytest.fixture(scope="session", autouse=True, name='database')
def database():
    DBUtils.init_test_db()
    db_connection.init_database(CONFIG['test_db_name'], CONFIG['db_user'])
    db_connection.connect()

    # Set database of the models
    db_siirtokarjalaistentie_models.set_database_to_models(db_connection.get_database())

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


@pytest.yield_fixture(autouse=True, scope='function', name='person_data')
def populate_person_information_to_db(database):
    config.CONFIG['anonymize'] = False
    DBUtils.truncate_db()
    # Person data is anonymized and tweaked and only usable for software testing.
    update_report.setup('testfile.json')
    return population_utils.populate_from_json(database, "./tests/populate/data/person.json")

# TODO: Add a good way to easily initialize test db either empty or filled one still defaulting to prefilled db
