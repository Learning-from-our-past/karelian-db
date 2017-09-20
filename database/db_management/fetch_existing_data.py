from database.db_management.models.db_siirtokarjalaistentie_models import *


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

    return {
        'primary_person': primary_person,
        'spouse_person': _fetch_primary_person(person_entry['spouse']['kairaId'])
    }
