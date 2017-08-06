import pytest
from peewee import Using
from db_management.models.db_siirtokarjalaistentie_models import Person, Marriage
from tests.utils.population_utils import load_json
from db_management.update_database import update_data_in_db
import config


# FIXME: Once population from new format is supported, this can be removed and simply use
# the person_data from main fixture
@pytest.yield_fixture(autouse=True, scope='module', name='person_data_new_format')
def new_json_format():
    config.CONFIG['anonymize'] = False
    return load_json("./tests/populate/data/person2.json")


def should_map_changes_in_json_to_model(person_data_new_format):
    person_models = []

    # Force some changes
    person_data_new_format[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
    person_data_new_format[0]['primaryPerson']['name']['surname'] = 'JAAKKOLA'
    person_data_new_format[0]['primaryPerson']['birthLocation']['locationName'] = 'Kuolemajärvi'
    person_data_new_format[0]['primaryPerson']['profession'] = 'Kirvesmies'
    person_data_new_format[0]['spouse']['firstNames'] = 'SAANA'
    person_data_new_format[0]['spouse']['weddingYear'] = '1969'

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


def should_not_change_fields_which_were_edited_by_human(person_data_new_format, researcher_connection):
    person = Person.get(Person.kairaId == person_data_new_format[0]['primaryPerson']['kairaId'])
    spouse = Person.get(Person.kairaId == person_data_new_format[0]['spouse']['kairaId'])
    marriage = Marriage.get(Marriage.manId == person.id)

    with Using(researcher_connection, [Person, Marriage]):
        # Save change to user with researcher user's connection
        person.firstName = 'Kalle'
        person.save()

        spouse.firstName = 'Sari'
        spouse.save()

        marriage.weddingYear = 1999
        marriage.save()

    person_models = []

    # Force some changes
    person_data_new_format[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
    person_data_new_format[0]['primaryPerson']['name']['surname'] = 'JAAKKOLA'
    person_data_new_format[0]['spouse']['firstNames'] = 'SAANA'
    person_data_new_format[0]['spouse']['weddingYear'] = '1911'

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
        assert person_models[0].primaryPerson == True
