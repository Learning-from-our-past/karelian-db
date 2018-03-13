"""
These are functions which can be used in json schema's preprocess part. Usually these should be
used to run data transformations and validations for the whole data object before the single data field
operations will be ran.

An example of this is a case where children are populated to the db. Before population, we need to check if ANY child
has manual made change in the db. If they have, we should cancel updating all children. To do this, we need to inspect
all children before trying to insert any of them. This is a task suitable to be ran before actual population.
"""
import nltk.stem.snowball as snowball

from common.siirtokarjalaistentie_models import *
from db_management.update_report import update_report
from db_management.exceptions import DataEntryValidationException

stemmer = snowball.SnowballStemmer('finnish')


def validate_children_list(children_list, data_entry, extra_data):
    """
    Before running any updates, check if the database has any manual changes for children. If ANY child has changes,
    skip all updates to all children.
    :return:
    """

    existing_children = Child.select().where(
        (Child.fatherId == extra_data['primary_person'].id) | (Child.motherId == extra_data['primary_person'].id)).order_by(Child.kairaId)

    # We do not want to delete or edit children who were manually edited
    for child in existing_children:
        if len(child.get_non_editable_fields()) > 0:
            # The kid has been changed manually, raise an error
            update_report.ignored_record_in('Child', len(existing_children))
            raise DataEntryValidationException

    # If no Child was edited, check if the new json will have any changes to the existing records. If not, no need to anything.
    if len(existing_children) > 0:
        change_detected = False

        def _get_existing_stemmed(child):
            if child is not None and child.birthPlaceId is not None:
                return child.birthPlaceId.stemmedName
            else:
                return 'None'

        def _get_place_name(place):
            if place is not None and place != '':
                return stemmer.stem(place)
            else:
                return 'None'

        def _sex(field_value):
            format_for_db = ''
            if field_value == 'Male':
                format_for_db = 'm'
            elif field_value == 'Female':
                format_for_db = 'f'

            return format_for_db

        if len(existing_children) != len(children_list):
            change_detected = True
        else:
            def _anon(name):
                return 'none' if CONFIG['anonymize'] else str(name)

            # Compare existing children and json children by using keys from their fields.
            # This won't take in account details of Places. Only their stemmed names.
            existing_children_by_key = {'{}_{}_{}_{}_{}_{}'.format(
                child.kairaId,
                _anon(child.firstName),
                _anon(child.lastName),
                _get_existing_stemmed(child),
                child.birthYear,
                child.sex): True
                for child in existing_children}

            new_children_keys = ['{}_{}_{}_{}_{}_{}'.format(
                child['kairaId'],
                _anon(child['name']),
                _anon(extra_data['primary_person'].lastName),
                _get_place_name(child['location']['locationName']),
                child['birthYear'],
                _sex(child['gender'])) for child in children_list]

            for key in new_children_keys:
                if key not in existing_children_by_key:
                    change_detected = True
                    break

        if change_detected and len(existing_children) > 0:
            _delete_children_of_person(extra_data['primary_person'])
        else:
            # No changes, so we do not need to populate children at all. Skip the whole child population process to save time.
            raise DataEntryValidationException

    # Create new empty Child models to be used during the population
    child_models = [Child() for c in children_list]

    return child_models, children_list


def _delete_children_of_person(primary_person):
    Child.delete().where((Child.fatherId == primary_person.id) | (Child.motherId == primary_person.id)).execute()
