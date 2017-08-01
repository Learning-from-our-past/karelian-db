from db_management.models.db_siirtokarjalaistentie_models import *


def _fetch_primary_person(kaira_id):
    try:
        return Person.get(Person.kairaId == kaira_id)
    except Person.DoesNotExist:
        return None


def _fetch_spouse_person(kaira_id):
    try:
        return Person.get(Person.kairaId == kaira_id)
    except Person.DoesNotExist:
        return None


def _fetch_children(children_kaira_ids):
    return Child.select().where(Child.kairaId << children_kaira_ids)


def _fetch_marriage(primary_person):
    if primary_person is not None:
        marriages = Marriage.select().where((Marriage.manId == primary_person.id) | (Marriage.womanId == primary_person.id))

        if len(marriages) == 1:
            return marriages[0]
        elif len(marriages) == 0:
            return None
        else:
            raise Exception('Updating multiple Marriages is not supported yet!')


def fetch_existing_data_of_person_entry(person_entry):
    primary_person = _fetch_primary_person(person_entry['kairaId']['results'])

    return {
        'primary_person': primary_person,
        'spouse_person': _fetch_primary_person(person_entry['spouse']['results']['kairaId']),
        'marriage': _fetch_marriage(primary_person),
        'children': _fetch_children([child['kairaId'] for child in person_entry['children']['results']['children']])
    }
