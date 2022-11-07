from db_management.divaevi_models import *
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
        value = getattr(data_entry, actual_attribute)
        if value is not None:
            value = value[int(index)]
    else:
        value = getattr(data_entry, attribute)
    return value


pickle_to_divaevi_person = {
    'model': DivaeviPerson,
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
    }
}
