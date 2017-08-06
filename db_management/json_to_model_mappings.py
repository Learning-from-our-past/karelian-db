from db_management.models.db_siirtokarjalaistentie_models import *
from config import CONFIG
import db_management.location_operations as loc

def map_value_to_model(key, model, field_value, data_entry):
    # Simply set the value to the model.
    setattr(model, key, field_value)
    return model, field_value


def anonymize(key, model, field_value, _data_entry):
    return model, None if CONFIG['anonymize'] else field_value


def transform_sex(key, model, field_value, data_entry):
    format_for_db = ''

    if field_value == 'Male':
        format_for_db = 'm'
    elif field_value == 'Female':
        format_for_db = 'f'

    return model, format_for_db


def invert_sex(key, model, field_value, data_entry):
    format_for_db = ''

    if field_value == 'Male':
        format_for_db = 'Female'
    elif field_value == 'Female':
        format_for_db = 'Male'

    return model, format_for_db


def set_primary_person(state):
    def _set_status(key, model, field_value, data_entry):
        return model, state

    return _set_status


def set_none(key, model, field_value, data_entry):
    return model, None


def convert_boolean_none(key, model, value, data_entry):
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


def add_profession(key, model, profession, data_entry):
    if profession is None:
        return model, None
    else:
        return model, Profession.get_or_create(name=profession)[0].id


def add_page(key, model, page_number, data_entry):
    return model, Page.get_or_create(pageNumber=page_number)[0].pageNumber


def add_marriage(key, models, wedding_year_input, data_entry):
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

        if 'weddingYear' in marriage.get_editable_fields():
            marriage.weddingYear = wedding_year_input or None

        marriage.save()

    return models, wedding_year_input


json_to_primary_person = {
    'model': Person,
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
    }
}

json_to_spouse = {
    'model': Person,
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
    'mappings': {
        'kairaId': {
            'json_path': ['kairaId'],
            'operations': [map_value_to_model]
        },
        'birthYear': {
            'json_path': ['birthYear'],
            'operations': [map_value_to_model]
        },
        'firstName': {
            'json_path': ['name'],
            'operations': [map_value_to_model]
        },
        'lastName': {
            'json_path': ['primaryPerson', 'name', 'surname'],
            'operations': [map_value_to_model]
        },
        'sourceTextId': {
            'json_path': ['personMetadata', 'sourceText'],
            'operations': [map_value_to_model]
        },
        'sex': {
            'json_path': ['gender'],
            'operations': [map_value_to_model]
        }
    }
}
