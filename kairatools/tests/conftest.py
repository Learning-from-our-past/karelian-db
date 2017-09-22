import pytest

import common.siirtokarjalaistentie_models as db_siirtokarjalaistentie_models
import common.testing.population_utils as population_utils
import database.config as config
from common.db_connection import db_connection
from common.testing.dbUtils import DBUtils
from database.tests.test_config import CONFIG
from kairatools.app import get_app


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


@pytest.fixture(scope="session", autouse=True, name='_database')
def _database():
    # FIXME: There is improvement to be done here. The test data population should probably be done
    # with init - postgres, populate_person_data - kaira, start up kairatools app - <something else>
    # Now everything is done with Postgres user since for some reason resetting the db_connection with a different
    # user takes LOOOOONG time during the tests. Replacing the connection or running data population in a special context
    # did not seem to help either.
    # The root problem might be the singleton nature of the db_connection.
    # Perhaps the solution would be get rid of it and check if Peewee offers the same functionality in form of
    # thread specific connections...?
    DBUtils.init_test_db()
    db_connection.init_database(CONFIG['test_db_name'], CONFIG['admin_user'])
    db_connection.connect()

    # Setup Kaira-db models
    db_siirtokarjalaistentie_models.set_database_to_models(db_connection.get_database())
    return db_connection.get_database()


@pytest.yield_fixture(autouse=True, scope='function', name='person_data')
def populate_person_information_to_db(_database):
    config.CONFIG['anonymize'] = False
    DBUtils.truncate_db()
    data = population_utils.populate_from_json(db_connection.get_database(), "./database/tests/populate/data/person2.json")
    db_connection.close()
    return data


@pytest.yield_fixture(autouse=True, scope='function', name='app')
def app(person_data):  # person_data as param to force it be ran before this one to let person populating to do its job first
    app = get_app()

    with app.app_context():
        yield app.test_client()
        db_connection.close()
