from db_management.models.db_siirtokarjalaistentie_models import *
from db_management.exceptions import *
from config import CONFIG
import db_management.location_operations as loc
import db_management.preprocess_operations as preproc
from playhouse.shortcuts import model_to_dict


def map_value_to_model(key, model, field_value, data_entry, extra_data):
    # Simply set the value to the model.
    existing_values = model_to_dict(model, recurse=False)

    if existing_values[key] != field_value:
        setattr(model, key, field_value)

    return model, field_value


def anonymize(key, model, field_value, data_entry, extra_data):
    return model, None if CONFIG['anonymize'] else field_value


def transform_sex(key, model, field_value, data_entry, extra_data):
    format_for_db = ''

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
    if profession is None:
        return model, None
    else:
        return model, Profession.get_or_create(name=profession)[0].id


def add_page(key, model, page_number, data_entry, extra_data):
    return model, Page.get_or_create(pageNumber=page_number)[0].pageNumber


def add_marriage(key, models, wedding_year_input, data_entry, extra_data):
    primary = models['primary']
    spouse = models['main']

    male = None
    female = None

    if primary.sex == 'm':
        male = primary
        female = spouse
    elif primary.sex == 'f':
        male = spouse
        female = primary

    if male and female:
        try:
            marriage = Marriage.get(Marriage.manId == male.id, Marriage.womanId == female.id)
        except DoesNotExist:
            marriage = Marriage()

        if marriage.get_editable_fields() is not None:
            if 'weddingYear' in marriage.get_editable_fields():
                marriage.weddingYear = wedding_year_input or None
        else:
            marriage.weddingYear = wedding_year_input or None

        marriage.manId = male.id
        marriage.womanId = female.id
        marriage.save()

    return models, wedding_year_input


def get_parent_id(parent_to_get):
    """
       Set Child model's parent id by inspecting Person models passed
       to the extra_data field.
    """

    def _figure_gender_of_couple(person1, person2):
        if person1.sex == 'm':
            male = person1
            female = person2
        elif person1.sex == 'f':
            male = person2
            female = person1
        else:
            raise SexMissingException

        return {'male': male, 'female': female}

    def _get_id(key, model, input, data_entry, extra_data):
        try:
            parents = _figure_gender_of_couple(extra_data['primary_person'], extra_data['spouse'])
        except SexMissingException:
            # If parent gender could not be assigned, assume that Person is male.
            parents = {'male': extra_data['primary_person'], 'female': None}

        father_id = None
        mother_id = None

        if parents['male']:
            father_id = parents['male'].id

        if parents['female']:
            mother_id = parents['female'].id

        if parent_to_get == 'father':
            return model, father_id
        else:
            return model, mother_id

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
        'firstName': {
            'json_path': ['primaryPerson', 'name', 'firstNames'],
            'operations': [anonymize, map_value_to_model]
        },
        'lastName': {
            'json_path': ['primaryPerson', 'name', 'surname'],
            'operations': [anonymize, map_value_to_model]
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
        'prevLastName': {
            'json_path': ['primaryPerson', 'originalFamily'],
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
            'json_path': ['spouse', 'birthData', 'birthLocation'],
            'operations': [loc.add_place, map_value_to_model]
        },
        'deathYear': {
            'json_path': ['spouse', 'deathYear'],
            'operations': [map_value_to_model]
        },
        'firstName': {
            'json_path': ['spouse', 'firstNames'],
            'operations': [anonymize, map_value_to_model]
        },
        'lastName': {
            'json_path': ['primaryPerson', 'name', 'surname'],
            'operations': [anonymize, map_value_to_model]
        },
        'originalText': {
            'json_path': ['personMetadata', 'sourceText'],
            'operations': [anonymize, map_value_to_model]
        },
        'pageNumber': {
            'json_path': ['personMetadata', 'approximatePageNumber'],
            'operations': [map_value_to_model]
        },
        'prevLastName': {
            'json_path': ['spouse', 'originalFamily'],
            'operations': [anonymize, map_value_to_model]
        },
        'sex': {
            'json_path': ['primaryPerson', 'name', 'gender'],
            'operations': [invert_sex, transform_sex, map_value_to_model]
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
        'fatherId': {
            'json_path': [],
            'operations': [get_parent_id('father'), map_value_to_model]
        },
        'motherId': {
            'json_path': [],
            'operations': [get_parent_id('mother'), map_value_to_model]
        }
    }
}
