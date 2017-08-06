from db_management.models.db_siirtokarjalaistentie_models import *


def _fetch_primary_person(kaira_id):
    try:
        return Person.get(Person.kairaId == kaira_id)
    except Person.DoesNotExist:
        return Person()


def _fetch_spouse_person(kaira_id):
    try:
        return Person.get(Person.kairaId == kaira_id)
    except Person.DoesNotExist:
        return Person()


def _fetch_children(children_kaira_ids):
    return Child.select().where(Child.kairaId << children_kaira_ids)


def fetch_existing_data_of_person_entry(person_entry):
    primary_person = _fetch_primary_person(person_entry['primaryPerson']['kairaId'])

    return {
        'primary_person': primary_person,
        'spouse_person': _fetch_primary_person(person_entry['spouse']['kairaId']),
        'children': _fetch_children([child['kairaId'] for child in person_entry['children']])
    }
