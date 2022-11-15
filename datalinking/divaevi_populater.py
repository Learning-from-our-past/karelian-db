from tqdm import tqdm
from db_management.siirtokarjalaistentie_models import *
from db_management.update_report import update_report
from datalinking.divaevi_pickle_to_model_mappings import map_data_to_model, pickle_to_divaevi_person
from db_management.exceptions import NoKairaIdException


def populate_linked_data(database, data):
    database.set_autocommit(False)
    database.begin()

    database.execute_sql("""
    LOCK TABLE siirtokarjalaisten_tie."Person" IN SHARE ROW EXCLUSIVE MODE;
    """)

    with database.atomic():
        for person in tqdm(data):
            _update_data_in_db(person)

    update_report.save_report()
    database.commit()
    database.set_autocommit(True)
    database.close()


def _update_data_in_db(person_entry):
    if person_entry.link_kaira_id is None:
        raise NoKairaIdException('All DVV people populated into the database must have '
                                 'a matching kairaId from Mikarelia database.')
    existing_data = _fetch_existing_divaevi_person(person_entry)
    _update_divaevi_person_in_db(existing_data, person_entry)


def _update_divaevi_person_in_db(person_model, person_entry):
    divaevi_person = map_data_to_model(
        person_model, person_entry, pickle_to_divaevi_person)

    if divaevi_person.is_dirty():
        update_report.changed_record_in('DivaeviPerson')

    divaevi_person.save()
    if person_entry.link_kaira_id is not None:
        _set_divaevi_id_for_mikarelian_in_db(person_entry)


def _set_divaevi_id_for_mikarelian_in_db(person_entry):
    mikarelian = Person.get(Person.kairaId == person_entry.link_kaira_id)
    mikarelian.divaeviId = person_entry.db_id
    if mikarelian.is_dirty():
        update_report.changed_record_in('Person')
    mikarelian.save()


def _create_new_divaevi_person(person_entry):
    return _create_new_divaevi_person(person_entry)


def _fetch_existing_divaevi_person(person_entry):
    return _fetch_divaevi_person(person_entry.db_id)


def _fetch_divaevi_person(db_id):
    return DivaeviPerson.get_or_create(id=db_id)[0]


def _fetch_primary_person(kaira_id):
    try:
        return Person.get(Person.kairaId == link_kaira_id)
    except Person.DoesNotExist:
        return Person()


def fetch_existing_data_of_person_entry(person_entry):
    primary_person = _fetch_primary_person(
        person_entry['primaryPerson']['kairaId'])

    return {
        'primary_person': primary_person,
    }
