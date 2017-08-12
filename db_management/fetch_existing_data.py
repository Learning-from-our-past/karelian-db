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


def _fetch_children(primary_person, children_kaira_ids):
    if primary_person.id is not None:
        children = list(Child.select().where(
            (Child.fatherId == primary_person.id) | (Child.motherId == primary_person.id)).order_by(Child.kairaId))
    else:
        children = []

    # Add missing children by creating empty models for them
    if len(children) < len(children_kaira_ids):
        existing_children_ids = {child.kairaId for child in children}

        for kaira_id in children_kaira_ids:
            if kaira_id not in existing_children_ids:
                new_child = Child()
                new_child.kairaId = kaira_id
                children.append(new_child)

    return children


def fetch_existing_data_of_person_entry(person_entry):
    primary_person = _fetch_primary_person(person_entry['primaryPerson']['kairaId'])

    return {
        'primary_person': primary_person,
        'spouse_person': _fetch_primary_person(person_entry['spouse']['kairaId']),
        'children': _fetch_children(primary_person, [child['kairaId'] for child in person_entry['children']])
    }
