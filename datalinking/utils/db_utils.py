import db_management.siirtokarjalaistentie_models as db_siirtokarjalaistentie_models
import datalinking.models.katiha_models as db_katiha_models
from db_management.database_config import CONFIG
from db_management.db_connection import DbConnection
from db_management.siirtokarjalaistentie_models import Person
from db_management.katiha_models import *
from db_management.update_report import update_report
from peewee import fn


"""
A small utility to help connect to the DB during datalinking. Use as a context manager.
"""


class DbConnectionUtil:
    def __init__(self, db):
        db = db.casefold()
        if db == 'katiha':
            db_name = 'katiha'
            db_type = 'mysql'
            db_port = 3306
            models = db_katiha_models
        else:
            db_name = CONFIG['db_name']
            db_type = 'postgres'
            db_port = CONFIG['db_port']
            models = db_siirtokarjalaistentie_models
        self._models = models
        self._db_connection = DbConnection(db_type=db_type)
        self._db_connection.init_database(db_name=db_name, db_user=CONFIG['db_user'],
                                          host='localhost', port=db_port)
        self._database = None

    def __enter__(self):
        self._db_connection.connect()
        self._database = self._db_connection.get_database()
        self._models.set_database_to_models(self._database)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._database.close()


def get_family_remover():
    """
    If families need to be deleted (for example, if the link data has changed somehow and
    we need to remove people from the database), the function returned by this one can be
    used to delete families while keeping the update_report accurate.
    """
    family_to_num_linked_members = get_katiha_families_and_number_linked_family_members()

    def remove_family(to_remove):
        """
        Removes a family from the DB and handles update report stuff.
        """
        num_changed_person_records = next(
            (family.num_linked_members for family in family_to_num_linked_members
             if family.id == to_remove.id),
            None
        )
        Family.delete().where(Family.id == to_remove.id)
        if num_changed_person_records:
            num_changed_person_records = num_changed_person_records.num_linked_members
            update_report.changed_record_in('Person', num_changed_person_records)
    return remove_family


def get_family_ids_by_katiha_ids(katiha_ids):
    return (KatihaPerson.select(KatihaPerson.familyId)
            .where(KatihaPerson.id.in_(katiha_ids))
            .execute())


def get_set_of_katiha_ids_in_db():
    katiha_ids_in_db_result = KatihaPerson.select(KatihaPerson.id).execute()
    return {person.id for person in katiha_ids_in_db_result}


def get_katiha_families_and_number_linked_family_members(alias_for_count='num_linked_members'):
    return (
        Person.select(KatihaPerson.familyId,
                      fn.COUNT(KatihaPerson.familyId).alias(alias_for_count))
              .join(KatihaPerson)
              .where(KatihaPerson.familyId.is_null(False))
              .group_by(KatihaPerson.familyId)
              .execute()
    )


def get_katiha_families_with_zero_linked_family_members():
    katiha_families_with_linked_family_members = (
        Person.select(KatihaPerson.familyId)
              .join(KatihaPerson)
              .where(KatihaPerson.familyId.is_null(False))
              .group_by(KatihaPerson.familyId)
    )

    return (Family.select(Family.id)
            .where(Family.id.not_in(katiha_families_with_linked_family_members))
            .execute())