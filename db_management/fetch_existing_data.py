from db_management.siirtokarjalaistentie_models import *


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


def fetch_existing_data_of_person_entry(person_entry):
    primary_person = _fetch_primary_person(person_entry['primaryPerson']['kairaId'])
    spouse_person = None
    if person_entry['spouse']:
        spouse_person = _fetch_primary_person(person_entry['spouse']['kairaId'])

    return {
        'primary_person': primary_person,
        'spouse_person': spouse_person
    }
