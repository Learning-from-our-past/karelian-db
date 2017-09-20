import pytest
from database.db_management.models.db_siirtokarjalaistentie_models import *


class TestPersonEditLogging:
    @pytest.yield_fixture(autouse=True, scope='function')
    def person(self):
        return Person.get()

    def should_have_correct_initial_data_in_manual_edits_object(self, person):
        assert person.editLog['firstName']['author'] == 'kaira'
        assert person.editLog['firstName']['oldValue'] is None
        assert 'lastChanged' in person.editLog['firstName']

    def should_change_manual_edits_object_records_for_columns_which_were_edited(self, person):
        original_name = person.firstName
        original_log = person.editLog
        person.firstName = 'New name'
        person.save()

        person = Person.select().where(Person.kairaId == person.kairaId).get()

        assert person.editLog['firstName']['author'] == 'kaira'
        assert person.editLog['firstName']['oldValue'] == original_name
        assert person.editLog['firstName']['lastChanged'] != original_log['firstName']['lastChanged']

        # Last name should not have changed and time stamp should be intact
        assert person.editLog['lastName']['lastChanged'] == original_log['lastName']['lastChanged']


