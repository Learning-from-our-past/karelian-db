import pytest
from tests.utils.dbUtils import DBUtils
import tests.utils.population_utils as population_utils
from models.db_siirtokarjalaistentie_models import *


@pytest.yield_fixture(autouse=True, scope='module', name='person_data')
def populate_person_information_to_db():
    DBUtils.truncate_db()
    # Person data is anonymized and tweaked and only usable for software testing.
    return population_utils.populate_from_json("./tests/populate/data/person1.json")[0]

class TestPersonEditLogging:
    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def test_that_manual_edits_object_has_initial_data(self, person):
        assert person.editLog['firstName']['author'] == 'postgres'
        assert person.editLog['firstName']['oldValue'] is None
        assert person.editLog['firstName']['lastChanged']

    def test_that_manual_edits_object_records_change_to_only_edited_columns(self, person):
        original_name = person.firstName
        original_log = person.editLog
        person.firstName = 'New name'
        person.save()

        person = Person.select().where(Person.id == person.id).get()

        assert person.editLog['firstName']['author'] == 'postgres'
        assert person.editLog['firstName']['oldValue'] == original_name
        assert person.editLog['firstName']['lastChanged'] != original_log['firstName']['lastChanged']

        # Last name should not have changed and time stamp should be intact
        assert person.editLog['lastName']['lastChanged'] == original_log['lastName']['lastChanged']


