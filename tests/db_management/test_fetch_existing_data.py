from db_management.fetch_existing_data import fetch_existing_data_of_person_entry


def should_fetch_existing_primary_details_of_person_and_children(person_data):
    result = fetch_existing_data_of_person_entry(person_data[0])

    assert result['primary_person'].kairaId == person_data[0]['kairaId']['results']
    assert result['spouse_person'].kairaId == person_data[0]['spouse']['results']['kairaId']
    assert len(result['children']) == 1
    assert result['children'][0].kairaId == person_data[0]['children']['results']['children'][0]['kairaId']
    assert result['marriage'].weddingYear == 1944


def should_return_None_for_person_who_does_not_exist():
    result = fetch_existing_data_of_person_entry({
        'kairaId': {'results': 'siirtokarjalaiset_1_102P'},
        'spouse': {'results': {'kairaId': 'siirtokarjalaiset_1_101S'}},
        'children': {'results': {'children': [{'kairaId': 'siirtokarjalaiset_1_103C'}]}}
    })

    assert result['primary_person'] is None
    assert result['spouse_person'] is None
    assert result['marriage'] is None
    assert len(result['children']) == 0


def should_return_marriage_and_spouse_as_None_if_person_is_unmarried(person_data):
    result = fetch_existing_data_of_person_entry(person_data[1])
    assert result['primary_person'].kairaId == person_data[1]['kairaId']['results']
    assert result['spouse_person'] is None
    assert result['marriage'] is None
    assert len(result['children']) == 0
