import pytest
from peewee import Using
from db_management.models.db_siirtokarjalaistentie_models import Person
from tests.utils.population_utils import load_json
from db_management.update_database import update_data_in_db


# FIXME: Once population from new format is supported, this can be removed and simply use
# the person_data from main fixture
@pytest.yield_fixture(autouse=True, scope='module', name='person_data_new_format')
def new_json_format():
    return load_json("./tests/populate/data/person2.json")


def should_map_changes_in_json_to_model(person_data_new_format):
    person_models = []

    # Force some changes
    person_data_new_format[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
    person_data_new_format[0]['primaryPerson']['name']['surname'] = 'JAAKKOLA'

    for data_entry in person_data_new_format:
        person_models.append(update_data_in_db(data_entry))

    assert person_models[0].firstName == person_data_new_format[0]['primaryPerson']['name']['firstNames']
    assert person_models[0].lastName == person_data_new_format[0]['primaryPerson']['name']['surname']

    # TODO: Check that changes were persisted to the db...


def should_not_change_fields_which_were_edited_by_human(person_data_new_format, researcher_connection):
    person = Person.get(Person.kairaId == person_data_new_format[0]['primaryPerson']['kairaId'])

    with Using(researcher_connection, [Person]):
        # Save change to user with researcher user's connection
        person.firstName = 'Kalle'
        person.save()

    person_models = []

    # Force some changes
    person_data_new_format[0]['primaryPerson']['name']['firstNames'] = 'JAAKKO JAKKE'
    person_data_new_format[0]['primaryPerson']['name']['surname'] = 'JAAKKOLA'

    for data_entry in person_data_new_format:
        person_models.append(update_data_in_db(data_entry))

    assert person_models[0].firstName == 'Kalle'    # Should have not changed.
    assert person_models[0].lastName == person_data_new_format[0]['primaryPerson']['name']['surname']

    # TODO: Check that changes were persisted to the db...
