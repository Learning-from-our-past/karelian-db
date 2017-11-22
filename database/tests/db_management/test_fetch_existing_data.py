import pytest
from database.db_management.fetch_existing_data import fetch_existing_data_of_person_entry


def should_fetch_existing_primary_details_of_person_and_children(person_data):
    result = fetch_existing_data_of_person_entry(person_data[0])

    assert result['primary_person'].kairaId == person_data[0]['primaryPerson']['kairaId']
    assert result['spouse_person'].kairaId == person_data[0]['spouse']['kairaId']


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


def should_return_spouse_as_none_if_person_is_unmarried(person_data):
    result = fetch_existing_data_of_person_entry(person_data[1])

    assert result['primary_person'].kairaId == person_data[1]['primaryPerson']['kairaId']
    assert result['primary_person'].firstName is not None
    assert result['spouse_person'] is None
