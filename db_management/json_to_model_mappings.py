from db_management.models.db_siirtokarjalaistentie_models import *
from config import CONFIG

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


def set_primary_person(key, model, field_value, data_entry):
    return model, True


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


def invert_sex(key, model, field_value, data_entry):
    return model, field_value

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
            'operations': [map_value_to_model]
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
            'operations': [set_primary_person, map_value_to_model]
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
            'operations': [map_value_to_model]
        },
        'sex': {
            'json_path': ['primaryPerson', 'name', 'gender'],
            'operations': [invert_sex, map_value_to_model]
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
