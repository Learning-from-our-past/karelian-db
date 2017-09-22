import common.testing.population_utils as population_utils
import pytest
from peewee_migrate import Router
from peewee import Using
import database.config as config
import database.db_management.models.db_siirtokarjalaistentie_models as db_siirtokarjalaistentie_models
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
    # Note this uses connection and utils from database/ project
    DBUtils.init_test_db()
    db_connection.init_database(CONFIG['test_db_name'], CONFIG['db_user'])
    db_connection.connect()
    # FIXME: Hypothesis
    # Likely first time this is ran, the database connection is gotten from database module which
    # has correct rights and other properties. Next in app fixture, the karelian models' database
    # is switched to kairatools one. Nex time we then run populate_person_information... fixture
    # the models have a wrong database connection which then breaks things in an unexpexted way.

    # Setup Kaira-db models
    db_siirtokarjalaistentie_models.set_database_to_models(db_connection.get_database())
    return db_connection.get_database()


@pytest.yield_fixture(autouse=True, scope='function', name='person_data')
def populate_person_information_to_db(_database):
    config.CONFIG['anonymize'] = False
    DBUtils.truncate_db()
    data = population_utils.populate_from_json(_database, "./database/tests/populate/data/person2.json")
    db_connection.close()
    return data


@pytest.yield_fixture(autouse=True, scope='function', name='app')
def app(person_data):  # person_data as param to force it be ran before this one to let person populating to do its job first
    app = get_app()
    print('fukken app')
    with app.app_context():
        # Run kaira-tools migrations
        router = Router(db_connection.get_database(), schema='kairatools', migrate_dir='kairatools/migrations')
        router.run()

        yield app.test_client()

        db_connection.close()

