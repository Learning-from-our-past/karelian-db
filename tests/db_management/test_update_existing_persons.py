import pytest
from peewee import Using
from playhouse.shortcuts import model_to_dict

import db_management.location_operations as loc_op
import db_management.preprocess_operations as preproc
from db_management.siirtokarjalaistentie_models import Person, Marriage, Child, LivingRecord, KairaUpdateReportModel, \
    FarmDetails
from db_management.testing.mikarelia_test_db_utils import MiKARELIADBUtils
from db_management.testing.population_utils import MockRecord
from db_management.update_database import update_data_in_db
from db_management.update_report import update_report


class TestUpdateOnExistingDb:

    def should_map_changes_in_json_to_model(self, person_data):
        person_models = []

        # Force some changes
        person_data[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
        person_data[0]['primaryPerson']['name']['surname'] = 'JAAKKOLA'
        person_data[0]['primaryPerson']['birthLocation']['locationName'] = 'Kuolemajärvi'
        person_data[0]['primaryPerson']['profession']['professionName'] = 'Kirvesmies'
        person_data[0]['spouse']['firstNames'] = 'SAANA'
        person_data[0]['spouse']['weddingYear'] = '1969'
        person_data[0]['children'][0]['birthYear'] = '1955'

        for data_entry in person_data:
            person_models.append(update_data_in_db(data_entry, MockRecord()))

        assert person_models[0].firstName == person_data[0]['primaryPerson']['name']['firstNames']
        assert person_models[0].lastName == person_data[0]['primaryPerson']['name']['surname']

        # Make sure the changes were persisted to the db
        primary_person = Person.select().where(Person.kairaId == person_models[0].kairaId)[0]
        assert primary_person.firstName == person_data[0]['primaryPerson']['name']['firstNames']
        assert primary_person.lastName == person_data[0]['primaryPerson']['name']['surname']
        assert primary_person.birthPlaceId.name == 'Kuolemajärvi'
        assert primary_person.professionId.name == 'Kirvesmies'

        # Spouse's name should have changed too
        spouse_person = Person.select().where(Person.kairaId == person_data[0]['spouse']['kairaId'])[0]
        assert spouse_person.firstName == 'SAANA'

        marriage = Marriage.get(Marriage.manId == primary_person.id)
        assert marriage.weddingYear == 1969

        child = Child.get(Child.firstName == person_data[0]['children'][0]['name'])
        assert child.motherId.id == spouse_person.id
        assert child.birthYear == 1955


class TestInsertingToEmptyDb(TestUpdateOnExistingDb):
    @pytest.yield_fixture(autouse=True, scope='function', name='truncate_db')
    def truncate(self):
        MiKARELIADBUtils.truncate_db()

    def should_add_living_records(self, person_data, mocker):
        person_models = []

        update_report.setup('should_add_living_records')

        delete_spy = mocker.patch('db_management.location_operations._delete_migration_history', autospec=True)

        for data_entry in person_data:
            person_models.append(update_data_in_db(data_entry, MockRecord()))

        update_report.save_report()

        assert delete_spy.call_count == 2   # "Delete" should be called for both persons since they are not in the db

        records_for_person = LivingRecord.select().where(LivingRecord.personId == person_models[0].id)
        assert len(records_for_person) == 5

        check_update_report('should_add_living_records', {
            'recordCountChange': {'Marriage': 1, 'Profession': 3, 'Child': 2, 'Place': 6,
                                  'Person': 3, 'Page': 1, 'LivingRecord': 10, 'KatihaPerson': 0,
                                  'Family': 0, 'Language': 0}
        })

    class TestChildren:

        def should_not_try_to_delete_anything_when_populating(self, person_data, mocker):
            person_models = []

            delete_spy = mocker.patch.object(preproc, '_delete_children_of_person',
                                             wraps=preproc._delete_children_of_person)

            for data_entry in person_data:
                person_models.append(update_data_in_db(data_entry, MockRecord()))

            assert delete_spy.call_count == 0


def check_update_report(name, expected):
    report = model_to_dict(KairaUpdateReportModel.get(KairaUpdateReportModel.kairaFileName == name))

    for key, value in expected.items():
        assert report[key] == value


class TestOnlyForExistingDataInDb:

    def should_not_change_fields_which_were_edited_by_human(self, person_data, researcher_connection):
        person = Person.get(Person.kairaId == person_data[0]['primaryPerson']['kairaId'])
        spouse = Person.get(Person.kairaId == person_data[0]['spouse']['kairaId'])
        marriage = Marriage.get(Marriage.manId == person.id)

        update_report.setup('should_not_change_fields_which_were_edited_by_human')

        with Using(researcher_connection, [Person, Marriage, Child]):
            # Save change to user with researcher user's connection
            person.firstName = 'Kalle'
            person.save()

            spouse.firstName = 'Sari'
            spouse.save()

            marriage.weddingYear = 1999
            marriage.save()

        person_models = []

        # Force some changes
        person_data[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
        person_data[0]['primaryPerson']['name']['surname'] = 'JAAKKOLA'
        person_data[0]['spouse']['firstNames'] = 'SAANA'
        person_data[0]['spouse']['weddingYear'] = '1911'

        for data_entry in person_data:
            person_models.append(update_data_in_db(data_entry, MockRecord()))

        update_report.save_report()

        assert person_models[0].firstName == 'Kalle'    # Should have not changed.
        assert person_models[0].lastName == person_data[0]['primaryPerson']['name']['surname']

        # Make sure the changes were persisted to the db but human made changes were not overridden
        primary_person_in_db = Person.get(Person.kairaId == person_models[0].kairaId)
        assert primary_person_in_db.firstName == 'Kalle'
        assert primary_person_in_db.lastName == person_data[0]['primaryPerson']['name']['surname']

        spouse_in_db = Person.get(Person.kairaId == person_data[0]['spouse']['kairaId'])
        assert spouse_in_db.firstName == 'Sari'

        marriage_in_db = Marriage.get(Marriage.manId == primary_person_in_db.id)
        assert marriage_in_db.weddingYear == 1999

        check_update_report('should_not_change_fields_which_were_edited_by_human', {
            'changedRecordsCount': {'Child': 0, 'Marriage': 0, 'LivingRecord': 0, 'Page': 0,
                                    'Place': 0, 'Person': 2, 'Profession': 0, 'KatihaPerson': 0,
                                    'Family': 0, 'Language': 0}
        })

    def should_not_do_anything_for_livingrecords_if_they_have_not_changed(self, person_data, mocker):
        person_models = []

        delete_spy = mocker.patch('db_management.location_operations._delete_migration_history', autospec=True)

        for data_entry in person_data:
            person_models.append(update_data_in_db(data_entry, MockRecord()))

        assert delete_spy.call_count == 0

    def should_repopulate_livingrecords_if_there_is_different_amount_of_them_in_db(self, person_data, mocker):
        person = Person.get(Person.kairaId == person_data[0]['primaryPerson']['kairaId'])

        # There should already be all records
        old_records = LivingRecord.select().where(LivingRecord.personId == person.id)
        assert len(old_records) == len(person_data[0]['primaryPerson']['migrationHistory']['locations'])

        # Remove one location from json
        person_data[0]['primaryPerson']['migrationHistory']['locations'] = \
            person_data[0]['primaryPerson']['migrationHistory']['locations'][1:]

        delete_spy = mocker.patch.object(loc_op, '_delete_migration_history', wraps=loc_op._delete_migration_history)

        for data_entry in person_data:
            update_data_in_db(data_entry, MockRecord())

        # Old records should have been deleted and new ones populated
        assert delete_spy.call_count == 1

        new_records = LivingRecord.select().where(LivingRecord.personId == person.id)
        assert len(new_records) == len(person_data[0]['primaryPerson']['migrationHistory']['locations'])

    def should_repopulate_livingrecords_if_they_do_not_contain_same_records_as_json(self, person_data, mocker):
        person = Person.get(Person.kairaId == person_data[0]['primaryPerson']['kairaId'])

        # Make a minor change to a single record
        person_data[0]['primaryPerson']['migrationHistory']['locations'][1]['movedIn'] = 12

        delete_spy = mocker.patch.object(loc_op, '_delete_migration_history', wraps=loc_op._delete_migration_history)

        for data_entry in person_data:
            update_data_in_db(data_entry, MockRecord())

        # Old records should have been deleted and new ones populated
        assert delete_spy.call_count == 1

        new_records = LivingRecord.select().where(LivingRecord.personId == person.id)
        assert len(new_records) == len(person_data[0]['primaryPerson']['migrationHistory']['locations'])

        found_updated_record = False
        for record in new_records:
            if record.movedIn == 12:
                found_updated_record = True
                break

        assert found_updated_record is True

    def should_not_create_duplicate_farm_details_when_repopulating(self, person_data):
        person_models = []

        # Check that there is at least one FarmDetail row in the database
        count_initial = FarmDetails.select().count()
        assert count_initial > 0

        # Make a small modification to FarmDetails to see that it will be updated.
        person_data[0]['farmDetails']['farmTotalArea'] = 666

        for data_entry in person_data:
            person_models.append(update_data_in_db(data_entry, MockRecord()))

        count_after = FarmDetails.select().count()
        assert count_after == count_initial

        # Check that the FarmDetails were updated. Do this through primaryPerson since later on there might be more
        # FarmDetails in the test db
        primary_person = Person.select().where(Person.kairaId == person_models[0].kairaId)[0]
        assert primary_person.farmDetailsId.farmTotalArea == 666

    class TestChildren:

        def should_skip_changes_to_all_children_if_one_has_been_manually_edited(self, person_data, researcher_connection):
            child_with_manual_edit = Child.get(Child.kairaId == person_data[0]['children'][0]['kairaId'])

            update_report.setup('should_skip_changes_to_all_children_if_one_has_been_manually_edited')

            with Using(researcher_connection, [Person, Marriage, Child]):
                # Save change to user with researcher user's connection
                child_with_manual_edit.firstName = 'Kaarlo'
                child_with_manual_edit.save()

            person_models = []

            # Force some changes
            person_data[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
            person_data[0]['children'][0]['name'] = 'Jooseppi'
            person_data[0]['children'][1]['name'] = 'Lissu'

            for data_entry in person_data:
                person_models.append(update_data_in_db(data_entry, MockRecord()))

            update_report.save_report()

            # Primary person should have changed
            assert person_models[0].firstName == 'JAAKKO JAKKE'

            children_models = list(Child.select().where((Child.fatherId == person_models[0].id) | (Child.motherId == person_models[0].id)).order_by(Child.kairaId))

            # Children shouldn't since Kaarlo was edited manually before
            assert children_models[0].firstName == 'Kaarlo'
            assert children_models[1].firstName == 'Lapsi2'

            check_update_report('should_skip_changes_to_all_children_if_one_has_been_manually_edited', {
                'ignoredRecordsCount': {'Marriage': 0, 'Person': 0, 'Child': 2, 'Profession': 0,
                                        'Page': 0, 'Place': 0, 'LivingRecord': 0, 'KatihaPerson': 0,
                                        'Family': 0, 'Language': 0}
            })

        def should_not_do_anything_for_children_if_they_have_not_changed(self, person_data, mocker):
            person_models = []

            delete_spy = mocker.patch.object(preproc, '_delete_children_of_person', wraps=preproc._delete_children_of_person)

            for data_entry in person_data:
                person_models.append(update_data_in_db(data_entry, MockRecord()))

            assert delete_spy.call_count == 0

        def should_repopulate_children_if_there_is_different_amount_of_them_in_db_than_in_json(self, person_data, mocker):
            person = Person.get(Person.kairaId == person_data[0]['primaryPerson']['kairaId'])

            # There should already be all children
            old_children = Child.select().where((Child.fatherId == person.id) | (Child.motherId == person.id)).order_by(Child.kairaId)
            assert len(old_children) == len(person_data[0]['children'])

            # Remove one child from json
            person_data[0]['children'] = person_data[0]['children'][1:]

            delete_spy = mocker.patch.object(preproc, '_delete_children_of_person',
                                             wraps=preproc._delete_children_of_person)

            for data_entry in person_data:
                update_data_in_db(data_entry, MockRecord())

            # Old records should have been deleted and new ones populated
            assert delete_spy.call_count == 1

            new_children = Child.select().where((Child.fatherId == person.id) | (Child.motherId == person.id)).order_by(Child.kairaId)
            assert len(new_children) == len(person_data[0]['children'])

        def should_repopulate_children_if_they_do_not_contain_same_records_as_json(self, person_data, mocker):
            person = Person.get(Person.kairaId == person_data[0]['primaryPerson']['kairaId'])

            # There should already be all children
            old_children = Child.select().where((Child.fatherId == person.id) | (Child.motherId == person.id)).order_by(
                Child.kairaId)
            assert len(old_children) == len(person_data[0]['children'])

            # Make a minor change to a single record
            person_data[0]['children'][0]['name'] = 'Repe'

            delete_spy = mocker.patch.object(preproc, '_delete_children_of_person',
                                             wraps=preproc._delete_children_of_person)

            for data_entry in person_data:
                update_data_in_db(data_entry, MockRecord())

            # Old records should have been deleted and new ones populated
            assert delete_spy.call_count == 1

            new_children = Child.select().where((Child.fatherId == person.id) | (Child.motherId == person.id)).order_by(
                Child.kairaId)
            assert len(new_children) == len(person_data[0]['children'])
            assert new_children[0].firstName == 'Repe'
            assert new_children[0].lastName == 'MIESSUKUNIMI'


class TestValueMapping:

    @pytest.yield_fixture(autouse=True, scope='function', name='person_models')
    def new_json_format(self, person_data):
        person_models = []

        for data_entry in person_data:
            person_models.append(update_data_in_db(data_entry, MockRecord()))

        return person_models

    def should_transform_sex_to_correct_format(self, person_models):
        assert person_models[0].sex == 'm'
        assert person_models[1].sex == 'm'

    def should_transform_certain_boolean_fields_to_strings(self, person_models):
        assert person_models[0].returnedKarelia == 'true'
        assert person_models[1].returnedKarelia == 'true'

    def should_set_person_as_primary(self, person_models):
        assert person_models[0].primaryPerson is True
