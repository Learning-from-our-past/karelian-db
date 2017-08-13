import pytest
from db_management.fetch_existing_data import fetch_existing_data_of_person_entry
from tests.utils.population_utils import load_json
import config


# FIXME: Once population from new format is supported, this can be removed and simply use
# the person_data from main fixture
@pytest.yield_fixture(autouse=True, scope='module', name='person_data_new_format')
def new_json_format():
    config.CONFIG['anonymize'] = False
    return load_json("./tests/populate/data/person2.json")


def should_fetch_existing_primary_details_of_person_and_children(person_data_new_format):
    result = fetch_existing_data_of_person_entry(person_data_new_format[0])

    assert result['primary_person'].kairaId == person_data_new_format[0]['primaryPerson']['kairaId']
    assert result['spouse_person'].kairaId == person_data_new_format[0]['spouse']['kairaId']


def should_return_empty_model_for_person_who_does_not_exist():
    result = fetch_existing_data_of_person_entry({
        'primaryPerson': {'kairaId': 'siirtokarjalaiset_1_102P'},
        'spouse': {'kairaId': 'siirtokarjalaiset_1_101S'},
        'children': [{'kairaId': 'siirtokarjalaiset_1_103C'}]
    })

    assert result['primary_person'] is not None
    assert result['primary_person'].firstName is None
    assert result['spouse_person'] is not None
    assert result['spouse_person'].firstName is None


def should_return_spouse_as_empty_model_if_person_is_unmarried(person_data_new_format):
    result = fetch_existing_data_of_person_entry(person_data_new_format[1])

    assert result['primary_person'].kairaId == person_data_new_format[1]['primaryPerson']['kairaId']
    assert result['primary_person'].firstName is not None
    assert result['spouse_person'].firstName is None
