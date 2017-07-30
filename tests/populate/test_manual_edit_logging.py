import pytest

import tests.utils.population_utils as population_utils
from db_management.models.db_siirtokarjalaistentie_models import *
from tests.utils.dbUtils import DBUtils


@pytest.yield_fixture(autouse=True, scope='module', name='person_data')
def populate_person_information_to_db():
    DBUtils.truncate_db()
    # Person data is anonymized and tweaked and only usable for software testing.
    return population_utils.populate_from_json("./tests/populate/data/person1.json")[0]

class TestPersonEditLogging:
    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def should_have_correct_initial_data_in_manual_edits_object(self, person):
        assert person.editLog['firstName']['author'] == 'kaira'
        assert person.editLog['firstName']['oldValue'] is None
        assert person.editLog['firstName']['lastChanged']

    def should_change_manual_edits_object_records_for_columns_which_were_edited(self, person):
        original_name = person.firstName
        original_log = person.editLog
        person.firstName = 'New name'
        person.save()

        person = Person.select().where(Person.id == person.id).get()

        assert person.editLog['firstName']['author'] == 'kaira'
        assert person.editLog['firstName']['oldValue'] == original_name
        assert person.editLog['firstName']['lastChanged'] != original_log['firstName']['lastChanged']

        # Last name should not have changed and time stamp should be intact
        assert person.editLog['lastName']['lastChanged'] == original_log['lastName']['lastChanged']


