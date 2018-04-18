from playhouse.shortcuts import model_to_dict

import db_management.location_operations as loc
import db_management.preprocess_operations as preproc
from db_management.exceptions import SexMissingException
from db_management.siirtokarjalaistentie_models import *


def map_value_to_model(key, model, field_value, data_entry, extra_data):
    # Simply set the value to the model.
    existing_values = model_to_dict(model, recurse=False)

    if existing_values[key] != field_value:
        setattr(model, key, field_value)

    return model, field_value


def anonymize(key, model, field_value, data_entry, extra_data):
    return model, None if CONFIG['anonymize'] else field_value


def transform_sex(key, model, field_value, data_entry, extra_data):
    format_for_db = None

    if field_value == 'Male':
        format_for_db = 'm'
    elif field_value == 'Female':
        format_for_db = 'f'

    return model, format_for_db


def invert_sex(key, model, field_value, data_entry, extra_data):
    format_for_db = ''

    if field_value == 'Male':
        format_for_db = 'Female'
    elif field_value == 'Female':
        format_for_db = 'Male'

    return model, format_for_db


def set_primary_person(state):
    def _set_status(key, model, field_value, data_entry, extra_data):
        return model, state

    return _set_status


def set_none(key, model, field_value, data_entry, extra_data):
    return model, None


def convert_boolean_none(key, model, value, data_entry, extra_data):
    """
    Convert boolean or None value to string of three different values. Reason being that
    MS Access can't make difference between NULL and False values of boolean field...
    :param value:
    :return:
    """
    result = 'false'

    if value is None:
        result = 'unknown'
    elif value is True:
        result = 'true'

    return model, result


def add_profession(key, model, profession, data_entry, extra_data):
    if profession['professionName'] is None:
        return model, None
    else:
        profession_model = Profession.get_or_create(name=profession['professionName'])[0]

        if profession['extraInfo'] is not None:
            # Extra info is not in the model
            profession_model.set_missing_properties(profession['extraInfo'])
            profession_model.save()

        return model, profession_model.id


def add_page(key, model, page_number, data_entry, extra_data):
    return model, Page.get_or_create(pageNumber=page_number)[0].pageNumber


def add_marriage(key, models, wedding_year_input, data_entry, extra_data):
    primary = models['primary']
    spouse = models['main']

    try:
        marriage = Marriage.get(Marriage.primaryId == primary.id, Marriage.spouseId == spouse.id)
    except DoesNotExist:
        marriage = Marriage()

    if marriage.get_editable_fields() is not None:
        if 'weddingYear' in marriage.get_editable_fields():
            marriage.weddingYear = wedding_year_input or None
    else:
        marriage.weddingYear = wedding_year_input or None

    marriage.primaryId = primary.id
    marriage.spouseId = spouse.id
    marriage.save()

    return models, wedding_year_input


def add_farm_details(is_primary_person):
    def _add_farm_details(key, person_model, farm_details_to_add, data_entry, extra_data):
        if is_primary_person:
            if farm_details_to_add is not None:
                if person_model.farmDetailsId is not None:
                    # Person might have farmDetails already. Get the id of the row and add it to the details so that
                    # we won't create a duplicate FarmDetails row when saving.
                    farm_details_to_add['id'] = person_model.farmDetailsId.id

                farm_details_model = FarmDetails(**farm_details_to_add)
                farm_details_model.save()
                return person_model, farm_details_model.id
            else:
                return person_model, None
        else:
            # For spouse just get the farm details id from primary person model where it was added
            # earlier.
            return person_model, extra_data['primary_person'].farmDetailsId

    return _add_farm_details


def get_parent_id(parent_to_get):
    """
    Set Child model's parent id by inspecting Person models passed
    to the extra_data field.
    """

    def _get_id(key, model, input, data_entry, extra_data):
        parent = None
        if parent_to_get == 'primary':
            parent = extra_data['primary_person'].id
        elif parent_to_get == 'spouse' and extra_data['spouse'] is not None:
            parent = extra_data['spouse'].id
        return model, parent

    return _get_id


def get_last_name_from_primary_person(key, model, wedding_year_input, data_entry, extra_data):
    return model, extra_data['primary_person']


json_to_primary_person = {
    'model': Person,
    'preprocess_operations': {
        'json_path': ['primaryPerson'],
        'operation': None
    },
    'mappings': {
        'kairaId': {
            'json_path': ['primaryPerson', 'kairaId'],
            'operations': [map_value_to_model]
        },
        'birthDay': {
            'json_path': ['primaryPerson', 'birthData', 'birthDay'],
            'operations': [map_value_to_model]
        },
        'birthMonth': {
            'json_path': ['primaryPerson', 'birthData', 'birthMonth'],
            'operations': [map_value_to_model]
        },
        'birthYear': {
            'json_path': ['primaryPerson', 'birthData', 'birthYear'],
            'operations': [map_value_to_model]
        },
        'birthPlaceId': {
            'json_path': ['primaryPerson', 'birthLocation'],
            'operations': [loc.add_place, map_value_to_model]
        },
        'professionId': {
            'json_path': ['primaryPerson', 'profession'],
            'operations': [add_profession, map_value_to_model]
        },
        'farmDetailsId': {
            'json_path': ['farmDetails'],
            'operations': [add_farm_details(True), map_value_to_model]
        },
        'firstName': {
            'json_path': ['primaryPerson', 'name', 'firstNames'],
            'operations': [anonymize, map_value_to_model]
        },
        'injuredInWar': {
            'json_path': ['primaryPerson', 'warData', 'injuredInWarFlag'],
            'operations': [map_value_to_model]
        },
        'lastName': {
            'json_path': ['primaryPerson', 'name', 'surname'],
            'operations': [anonymize, map_value_to_model]
        },
        'lotta': {
            'json_path': ['primaryPerson', 'warData', 'lottaActivityFlags', 'lotta'],
            'operations': [map_value_to_model]
        },
        'foodLotta': {
            'json_path': ['primaryPerson', 'warData', 'lottaActivityFlags', 'foodLotta'],
            'operations': [map_value_to_model]
        },
        'officeLotta': {
            'json_path': ['primaryPerson', 'warData', 'lottaActivityFlags', 'officeLotta'],
            'operations': [map_value_to_model]
        },
        'nurseLotta': {
            'json_path': ['primaryPerson', 'warData', 'lottaActivityFlags', 'nurseLotta'],
            'operations': [map_value_to_model]
        },
        'antiairLotta': {
            'json_path': ['primaryPerson', 'warData', 'lottaActivityFlags', 'antiairLotta'],
            'operations': [map_value_to_model]
        },
        'pikkulotta': {
            'json_path': ['primaryPerson', 'warData', 'lottaActivityFlags', 'pikkulotta'],
            'operations': [map_value_to_model]
        },
        'organizationLotta': {
            'json_path': ['primaryPerson', 'warData', 'lottaActivityFlags', 'organizationLotta'],
            'operations': [map_value_to_model]
        },
        'martta': {
            'json_path': ['primaryPerson', 'marttaActivityFlag'],
            'operations': [map_value_to_model]
        },
        'originalText': {
            'json_path': ['personMetadata', 'sourceText'],
            'operations': [anonymize, map_value_to_model]
        },
        'ownHouse': {
            'json_path': ['primaryPerson', 'ownHouse'],
            'operations': [map_value_to_model]
        },
        'pageNumber': {
            'json_path': ['personMetadata', 'approximatePageNumber'],
            'operations': [add_page, map_value_to_model]
        },
        'previousMarriages': {
            'json_path': ['primaryPerson', 'previousMarriagesFlag'],
            'operations': [convert_boolean_none, map_value_to_model]
        },
        'formerSurname': {
            'json_path': ['primaryPerson', 'formerSurname'],
            'operations': [anonymize, map_value_to_model]
        },
        'returnedKarelia': {
            'json_path': ['primaryPerson', 'migrationHistory', 'returnedToKarelia'],
            'operations': [convert_boolean_none, map_value_to_model]
        },
        'sex': {
            'json_path': ['primaryPerson', 'name', 'gender'],
            'operations': [transform_sex, map_value_to_model]
        },
        'servedDuringWar': {
            'json_path': ['primaryPerson', 'warData', 'servedDuringWarFlag'],
            'operations': [map_value_to_model]
        },
        'primaryPerson': {
            'json_path': [],
            'operations': [set_primary_person(True), map_value_to_model]
        }
    },
    'one_to_many': {
        'migrationHistory': {
            'json_path': ['primaryPerson', 'migrationHistory', 'locations'],
            'operations': [loc.create_migration_history]
        }
    }
}

json_to_spouse = {
    'model': Person,
    'preprocess_operations': {
        'json_path': ['spouse'],
        'operation': None
    },
    'mappings': {
        'kairaId': {
            'json_path': ['spouse', 'kairaId'],
            'operations': [map_value_to_model]
        },
        'birthDay': {
            'json_path': ['spouse', 'birthData', 'birthDay'],
            'operations': [map_value_to_model]
        },
        'birthMonth': {
            'json_path': ['spouse', 'birthData', 'birthMonth'],
            'operations': [map_value_to_model]
        },
        'birthYear': {
            'json_path': ['spouse', 'birthData', 'birthYear'],
            'operations': [map_value_to_model]
        },
        'birthPlaceId': {
            'json_path': ['spouse', 'birthLocation'],
            'operations': [loc.add_place, map_value_to_model]
        },
        'deathYear': {
            'json_path': ['spouse', 'death'],
            'operations': [map_value_to_model]
        },
        'farmDetailsId': {
            'json_path': [],
            'operations': [add_farm_details(False), map_value_to_model]
        },
        'firstName': {
            'json_path': ['spouse', 'firstNames'],
            'operations': [anonymize, map_value_to_model]
        },
        'injuredInWar': {
            'json_path': ['spouse', 'warData', 'injuredInWarFlag'],
            'operations': [map_value_to_model]
        },
        'lastName': {
            'json_path': ['primaryPerson', 'name', 'surname'],
            'operations': [anonymize, map_value_to_model]
        },
        'lotta': {
            'json_path': ['spouse', 'warData', 'lottaActivityFlags', 'lotta'],
            'operations': [map_value_to_model]
        },
        'foodLotta': {
            'json_path': ['spouse', 'warData', 'lottaActivityFlags', 'foodLotta'],
            'operations': [map_value_to_model]
        },
        'officeLotta': {
            'json_path': ['spouse', 'warData', 'lottaActivityFlags', 'officeLotta'],
            'operations': [map_value_to_model]
        },
        'nurseLotta': {
            'json_path': ['spouse', 'warData', 'lottaActivityFlags', 'nurseLotta'],
            'operations': [map_value_to_model]
        },
        'antiairLotta': {
            'json_path': ['spouse', 'warData', 'lottaActivityFlags', 'antiairLotta'],
            'operations': [map_value_to_model]
        },
        'pikkulotta': {
            'json_path': ['spouse', 'warData', 'lottaActivityFlags', 'pikkulotta'],
            'operations': [map_value_to_model]
        },
        'organizationLotta': {
            'json_path': ['spouse', 'warData', 'lottaActivityFlags', 'organizationLotta'],
            'operations': [map_value_to_model]
        },
        'martta': {
            'json_path': ['spouse', 'marttaActivityFlag'],
            'operations': [map_value_to_model]
        },
        'originalText': {
            'json_path': ['personMetadata', 'sourceText'],
            'operations': [anonymize, map_value_to_model]
        },
        'pageNumber': {
            'json_path': ['personMetadata', 'approximatePageNumber'],
            'operations': [map_value_to_model]
        },
        'formerSurname': {
            'json_path': ['spouse', 'formerSurname'],
            'operations': [anonymize, map_value_to_model]
        },
        'sex': {
            'json_path': ['primaryPerson', 'name', 'gender'],
            'operations': [invert_sex, transform_sex, map_value_to_model]
        },
        'servedDuringWar': {
            'json_path': ['spouse', 'warData', 'servedDuringWarFlag'],
            'operations': [map_value_to_model]
        },
        'primaryPerson': {
            'json_path': [],
            'operations': [set_primary_person(False), map_value_to_model]
        },
        'professionId': {
            'json_path': ['spouse', 'profession'],
            'operations': [add_profession, map_value_to_model]
        },
        'returnedKarelia': {
            'json_path': [],
            'operations': [set_none, convert_boolean_none, map_value_to_model]
        },
        'previousMarriages': {
            'json_path': [],
            'operations': [set_none, convert_boolean_none, map_value_to_model]
        },
    },
    'one_to_many': {
        'marriage': {
            'json_path': ['spouse', 'weddingYear'],
            'operations': [add_marriage]
        }
    }
}

json_to_child = {
    'model': Child,
    'preprocess_operations': {
        'json_path': ['children'],
        'operation': preproc.validate_children_list
    },
    'mappings': {
        'kairaId': {
            'json_path': ['children', '*', 'kairaId'],
            'operations': [map_value_to_model]
        },
        'birthYear': {
            'json_path': ['children', '*', 'birthYear'],
            'operations': [map_value_to_model]
        },
        'birthPlaceId': {
            'json_path': ['children', '*', 'location'],
            'operations': [loc.add_place, map_value_to_model]
        },
        'firstName': {
            'json_path': ['children', '*', 'name'],
            'operations': [anonymize, map_value_to_model]
        },
        'lastName': {
            'json_path': ['primaryPerson', 'name', 'surname'],
            'operations': [anonymize, map_value_to_model]
        },
        'sourceTextId': {
            'json_path': ['personMetadata', 'sourceText'],
            'operations': [map_value_to_model]
        },
        'sex': {
            'json_path': ['children', '*', 'gender'],
            'operations': [transform_sex, map_value_to_model]
        },
        'primaryParentId': {
            'json_path': [],
            'operations': [get_parent_id('primary'), map_value_to_model]
        },
        'spouseParentId': {
            'json_path': [],
            'operations': [get_parent_id('spouse'), map_value_to_model]
        }
    }
}
