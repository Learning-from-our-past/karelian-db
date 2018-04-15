from db_management.katiha_models import *
from db_management.json_to_model_mappings import map_value_to_model


def map_data_to_model(model, data_entry, mapping_operations, extra_data=None):
    for key, field_details in mapping_operations['mappings'].items():
        result_of_operation = _get_attr_from_namedtuple(data_entry,
                                                        field_details['namedtuple_attribute'])
        for operation in field_details['operations']:
            model, result_of_operation = operation(key, model, result_of_operation, data_entry, extra_data)
    return model


def _get_attr_from_namedtuple(data_entry, attribute):
    if ',' in attribute:
        actual_attribute, index = attribute.split(',')
        value = getattr(data_entry, actual_attribute)[int(index)]
    else:
        value = getattr(data_entry, attribute)
    return value


def _add_language(key, model, language, data_entry, extra_data):
    if language is None:
        return model, None
    else:
        language_model = Language.get_or_create(language=language)[0]
        return model, language_model.id


def _add_family(key, model, family_number, data_entry, extra_data):
    if family_number is None:
        return model, None
    else:
        family_model = Family.get_or_create(id=family_number)[0]
        return model, family_model.id


def _add_birth_in_marriage_code(key, model, birth_in_marriage_code, data_entry, extra_data):
    if birth_in_marriage_code is None:
        return model, None
    else:
        birth_in_marriage_model = BirthInMarriageCode.get_or_create(birthType=birth_in_marriage_code)[0]
        return model, birth_in_marriage_model.code


pickle_to_katiha_person = {
    'model': KatihaPerson,
    'mappings': {
        'birthDay': {
            'namedtuple_attribute': 'date_of_birth,0',
            'operations': [map_value_to_model]
        },
        'birthMonth': {
            'namedtuple_attribute': 'date_of_birth,1',
            'operations': [map_value_to_model]
        },
        'birthYear': {
            'namedtuple_attribute': 'date_of_birth,2',
            'operations': [map_value_to_model]
        },
        'motherLanguageId': {
            'namedtuple_attribute': 'mother_language',
            'operations': [_add_language, map_value_to_model]
        },
        'familyId': {
            'namedtuple_attribute': 'family_id',
            'operations': [_add_family, map_value_to_model]
        },
        'sex': {
            'namedtuple_attribute': 'sex',
            'operations': [map_value_to_model]
        },
        'birthInMarriage': {
            'namedtuple_attribute': 'birth_in_marriage',
            'operations': [_add_birth_in_marriage_code, map_value_to_model]
        },
        'multipleBirth': {
            'namedtuple_attribute': 'multiple_birth',
            'operations': [map_value_to_model]
        }
    }
}
