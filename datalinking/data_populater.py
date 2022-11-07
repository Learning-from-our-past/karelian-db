from tqdm import tqdm
from db_management.siirtokarjalaistentie_models import *
from datalinking.pickle_to_model_mappings import *
from db_management.update_report import update_report
from db_management.exceptions import NoFamilyIdAndKairaIdException
from datalinking.utils.db_utils import get_katiha_families_with_zero_linked_family_members
from datalinking.utils.db_utils import get_family_remover
from datalinking.utils.db_utils import get_set_of_katiha_ids_in_db
from datalinking.utils.db_utils import get_family_ids_by_katiha_ids


def populate_linked_data(database, data):
    database.set_autocommit(False)
    database.begin()

    database.execute_sql("""
    LOCK TABLE siirtokarjalaisten_tie."Person" IN SHARE ROW EXCLUSIVE MODE;
    """)

    with database.atomic():
        _remove_katiha_people_not_in_pickle_from_db(data)
        for person in tqdm(data):
            _update_data_in_db(person)

    _remove_unused_languages_and_families()

    update_report.save_report()
    database.commit()
    database.set_autocommit(True)
    database.close()


def _update_data_in_db(person_entry):
    if person_entry.link_kaira_id is None and person_entry.family_id is None:
        raise NoFamilyIdAndKairaIdException('All Katiha people populated into the DB must have '
                                            'either a familyId or a kairaId.')
    existing_data = _fetch_existing_katiha_person(person_entry)
    _update_katiha_person_in_db(existing_data, person_entry)


def _update_katiha_person_in_db(person_model, person_entry):
    katiha_person = map_data_to_model(person_model, person_entry, pickle_to_katiha_person)

    if katiha_person.is_dirty():
        update_report.changed_record_in('KatihaPerson')

    katiha_person.save()
    if person_entry.link_kaira_id is not None:
        _set_katiha_id_for_mikarelian_in_db(person_entry)


def _set_katiha_id_for_mikarelian_in_db(person_entry):
    mikarelian = Person.get(Person.kairaId == person_entry.link_kaira_id)
    mikarelian.katihaId = person_entry.db_id
    if mikarelian.is_dirty():
        update_report.changed_record_in('Person')
    mikarelian.save()


def _fetch_existing_katiha_person(person_entry):
    return _fetch_katiha_person(person_entry.db_id)


def _fetch_katiha_person(db_id):
    return KatihaPerson.get_or_create(id=db_id)[0]

def _fetch_divaevi_person(db_id):
    return DivaeviPerson.get_or_create()


def _remove_katiha_people_not_in_pickle_from_db(data):
    """
    Determines which Katiha people are in the database but not in the pickle, and then deletes
    the people in the database that are not present in the pickle.
    """
    katiha_ids_in_link_data = {person.db_id for person in data}
    katiha_ids_in_db = get_set_of_katiha_ids_in_db()
    katiha_ids_not_in_link_data = tuple(katiha_ids_in_db - katiha_ids_in_link_data)
    family_ids_of_people_not_in_link_data = get_family_ids_by_katiha_ids(katiha_ids_not_in_link_data)
    remove_linkless_family = get_family_remover()

    for katiha_id, family_id in zip(katiha_ids_not_in_link_data, family_ids_of_people_not_in_link_data):
        KatihaPerson.delete().where(KatihaPerson.id == katiha_id).execute()
        if family_id is None:
            # All katihalians in our DB with NULL familyId have a link by default
            # because the only non-linked katihalians in the DB are ones in families.
            update_report.changed_record_in('Person')

    no_linked_family_members = get_katiha_families_with_zero_linked_family_members()

    for result in no_linked_family_members:
        remove_linkless_family(result)


def _remove_unused_languages_and_families():
    """
    Cleans up languages and families that are not referenced from other tables.
    """
    unused_languages = (Language.select(Language.id)
                        .where(Language.id.not_in(KatihaPerson
                                                  .select(KatihaPerson.motherLanguageId)
                                                  .distinct()
                                                  .where(KatihaPerson.motherLanguageId.is_null(False)))))
    Language.delete().where(Language.id.in_(unused_languages)).execute()

    unused_families = (Family.select(Family.id)
                       .where(Family.id.not_in(KatihaPerson.select(KatihaPerson.familyId)
                                               .distinct()
                                               .where(KatihaPerson.familyId.is_null(False)))))
    Family.delete().where(Family.id.in_(unused_families)).execute()
