from db_management.models.db_siirtokarjalaistentie_models import *


def map_value_to_model(key, model, field_value, data_entry):
    # Simply set the value to the model.
    setattr(model, key, field_value)
    return model, field_value


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
            'operations': [map_value_to_model]
        },
        'lastName': {
            'json_path': ['primaryPerson', 'name', 'surname'],
            'operations': [map_value_to_model]
        },
        'originalText': {
            'json_path': [ 'personMetadata', 'sourceText'],
            'operations': [map_value_to_model]
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
            'operations': [map_value_to_model]
        },
        'prevLastName': {
            'json_path': ['primaryPerson', 'originalFamily'],
            'operations': [map_value_to_model]
        },
        'returnedKarelia': {
            'json_path': ['primaryPerson', 'migrationHistory', 'returnedToKarelia'],
            'operations': [map_value_to_model]
        },
        'sex': {
            'json_path': ['primaryPerson', 'name', 'gender'],
            'operations': [map_value_to_model]
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
            'operations': [map_value_to_model]
        },
        'lastName': {
            'json_path': ['primaryPerson', 'name', 'surname'],
            'operations': [map_value_to_model]
        },
        'originalText': {
            'json_path': ['personMetadata', 'sourceText'],
            'operations': [map_value_to_model]
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
