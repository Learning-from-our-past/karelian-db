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
    divaevi_person = None
    mikarelia_person = Person.get(Person.kairaId == link_kaira_id)
    if mikarelia_person.divaeviId is not None:
        divaevi_person = DivaeviPerson.get(
            DivaeviPerson.id == mikarelia_person.divaeviId)
    else:
        divaevi_person = DivaeviPerson()
        mikarelia_person.divaeviId = divaevi_person.id
        mikarelia_person.save()

    _update_divaevi_person_in_db(divaevi_person, person_entry)


def _update_divaevi_person_in_db(person_model, person_entry):
    divaevi_person = map_data_to_model(
        person_model, person_entry, pickle_to_divaevi_person)

    if divaevi_person.is_dirty():
        update_report.changed_record_in('DivaeviPerson')

    divaevi_person.save()
