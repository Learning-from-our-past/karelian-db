import pytest
import db_management.location_operations as loc_op
from peewee import Using
from db_management.models.db_siirtokarjalaistentie_models import Person, Marriage, Child, Livingrecord
from tests.utils.dbUtils import DBUtils
from tests.utils.population_utils import load_json
from db_management.update_database import update_data_in_db
import config


# FIXME: Once population from new format is supported, this can be removed and simply use
# the person_data from main fixture
@pytest.yield_fixture(autouse=True, scope='module', name='person_data_new_format')
def new_json_format():
    config.CONFIG['anonymize'] = False
    return load_json("./tests/populate/data/person2.json")


class TestUpdateOnExistingDb:

    def should_map_changes_in_json_to_model(self, person_data_new_format):
        person_models = []

        # Force some changes
        person_data_new_format[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
        person_data_new_format[0]['primaryPerson']['name']['surname'] = 'JAAKKOLA'
        person_data_new_format[0]['primaryPerson']['birthLocation']['locationName'] = 'Kuolemajärvi'
        person_data_new_format[0]['primaryPerson']['profession'] = 'Kirvesmies'
        person_data_new_format[0]['spouse']['firstNames'] = 'SAANA'
        person_data_new_format[0]['spouse']['weddingYear'] = '1969'
        person_data_new_format[0]['children'][0]['birthYear'] = '1955'

        for data_entry in person_data_new_format:
            person_models.append(update_data_in_db(data_entry))

        assert person_models[0].firstName == person_data_new_format[0]['primaryPerson']['name']['firstNames']
        assert person_models[0].lastName == person_data_new_format[0]['primaryPerson']['name']['surname']

        # Make sure the changes were persisted to the db
        primary_person = Person.select().where(Person.kairaId == person_models[0].kairaId)[0]
        assert primary_person.firstName == person_data_new_format[0]['primaryPerson']['name']['firstNames']
        assert primary_person.lastName == person_data_new_format[0]['primaryPerson']['name']['surname']
        assert primary_person.birthPlaceId.name == 'Kuolemajärvi'
        assert primary_person.professionId.name == 'Kirvesmies'

        # Spouse's name should have changed too
        spouse_person = Person.select().where(Person.kairaId == person_data_new_format[0]['spouse']['kairaId'])[0]
        assert spouse_person.firstName == 'SAANA'

        marriage = Marriage.get(Marriage.manId == primary_person.id)
        assert marriage.weddingYear == 1969

        child = Child.get(Child.fatherId == primary_person.id)
        assert child.motherId.id == spouse_person.id
        assert child.birthYear == 1955


class TestInsertingToEmptyDb(TestUpdateOnExistingDb):
    @pytest.yield_fixture(autouse=True, scope='function', name='truncate_db')
    def truncate(self):
        print('truncate')
        DBUtils.truncate_db()

    def should_add_living_records(self, person_data_new_format, mocker):
        person_models = []

        delete_spy = mocker.patch('db_management.location_operations._delete_migration_history', autospec=True)

        for data_entry in person_data_new_format:
            person_models.append(update_data_in_db(data_entry))

        assert delete_spy.call_count == 2   # "Delete" should be called for both persons since they are not in the db

        records_for_person = Livingrecord.select().where(Livingrecord.personId == person_models[0].id)
        assert len(records_for_person) == 5


class TestOnlyForExistingDataInDb:

    def should_not_change_fields_which_were_edited_by_human(self, person_data_new_format, researcher_connection):
        person = Person.get(Person.kairaId == person_data_new_format[0]['primaryPerson']['kairaId'])
        spouse = Person.get(Person.kairaId == person_data_new_format[0]['spouse']['kairaId'])
        marriage = Marriage.get(Marriage.manId == person.id)
        child = Child.get(Child.fatherId == person.id)

        with Using(researcher_connection, [Person, Marriage, Child]):
            # Save change to user with researcher user's connection
            person.firstName = 'Kalle'
            person.save()

            spouse.firstName = 'Sari'
            spouse.save()

            marriage.weddingYear = 1999
            marriage.save()

            child.firstName = 'Kaarlo'
            child.save()

        person_models = []

        # Force some changes
        person_data_new_format[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
        person_data_new_format[0]['primaryPerson']['name']['surname'] = 'JAAKKOLA'
        person_data_new_format[0]['spouse']['firstNames'] = 'SAANA'
        person_data_new_format[0]['spouse']['weddingYear'] = '1911'
        person_data_new_format[0]['children'][0]['name'] = 'Jooseppi'

        for data_entry in person_data_new_format:
            person_models.append(update_data_in_db(data_entry))

        assert person_models[0].firstName == 'Kalle'    # Should have not changed.
        assert person_models[0].lastName == person_data_new_format[0]['primaryPerson']['name']['surname']

        # Make sure the changes were persisted to the db but human made changes were not overridden
        primary_person_in_db = Person.get(Person.kairaId == person_models[0].kairaId)
        assert primary_person_in_db.firstName == 'Kalle'
        assert primary_person_in_db.lastName == person_data_new_format[0]['primaryPerson']['name']['surname']

        spouse_in_db = Person.get(Person.kairaId == person_data_new_format[0]['spouse']['kairaId'])
        assert spouse_in_db.firstName == 'Sari'

        marriage_in_db = Marriage.get(Marriage.manId == primary_person_in_db.id)
        assert marriage_in_db.weddingYear == 1999

        child_in_db = Child.get(Child.fatherId == person.id)
        assert child_in_db.firstName == 'Kaarlo'

    def should_not_do_anything_for_livingrecords_if_they_have_not_changed(self, person_data_new_format, mocker):
        person_models = []

        delete_spy = mocker.patch('db_management.location_operations._delete_migration_history', autospec=True)

        for data_entry in person_data_new_format:
            person_models.append(update_data_in_db(data_entry))

        assert delete_spy.call_count == 0

    def should_repopulate_livingrecords_if_there_is_different_amount_of_them_in_db(self, person_data_new_format, mocker):
        person = Person.get(Person.kairaId == person_data_new_format[0]['primaryPerson']['kairaId'])

        # There should already be all records
        old_records = Livingrecord.select().where(Livingrecord.personId == person.id)
        assert len(old_records) == len(person_data_new_format[0]['primaryPerson']['migrationHistory']['locations'])

        # Remove one location from json
        person_data_new_format[0]['primaryPerson']['migrationHistory']['locations'] = \
            person_data_new_format[0]['primaryPerson']['migrationHistory']['locations'][1:]

        delete_spy = mocker.patch.object(loc_op, '_delete_migration_history', wraps=loc_op._delete_migration_history)

        for data_entry in person_data_new_format:
            update_data_in_db(data_entry)

        # Old records should have been deleted and new ones populated
        assert delete_spy.call_count == 1

        new_records = Livingrecord.select().where(Livingrecord.personId == person.id)
        assert len(new_records) == len(person_data_new_format[0]['primaryPerson']['migrationHistory']['locations'])

    def should_repopulate_livingrecords_if_they_do_not_contain_same_records_as_json(self, person_data_new_format, mocker):
        person = Person.get(Person.kairaId == person_data_new_format[0]['primaryPerson']['kairaId'])

        # Make a minor change to a single record
        person_data_new_format[0]['primaryPerson']['migrationHistory']['locations'][1]['movedIn'] = 12

        delete_spy = mocker.patch.object(loc_op, '_delete_migration_history', wraps=loc_op._delete_migration_history)

        for data_entry in person_data_new_format:
            update_data_in_db(data_entry)

        # Old records should have been deleted and new ones populated
        assert delete_spy.call_count == 1

        new_records = Livingrecord.select().where(Livingrecord.personId == person.id)
        assert len(new_records) == len(person_data_new_format[0]['primaryPerson']['migrationHistory']['locations'])

        found_updated_record = False
        for record in new_records:
            if record.movedIn == 12:
                found_updated_record = True
                break

        assert found_updated_record is True


class TestValueMapping:

    @pytest.yield_fixture(autouse=True, scope='function', name='person_models')
    def new_json_format(self, person_data_new_format):
        person_models = []

        for data_entry in person_data_new_format:
            person_models.append(update_data_in_db(data_entry))

        return person_models

    def should_transform_sex_to_correct_format(self, person_models):
        assert person_models[0].sex == 'm'
        assert person_models[1].sex == 'm'

    def should_transform_certain_boolean_fields_to_strings(self, person_models):
        assert person_models[0].returnedKarelia == 'true'
        assert person_models[1].returnedKarelia == 'true'

    def should_set_person_as_primary(self, person_models):
        assert person_models[0].primaryPerson is True
