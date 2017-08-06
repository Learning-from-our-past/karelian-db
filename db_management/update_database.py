from db_management.fetch_existing_data import fetch_existing_data_of_person_entry
from db_management.json_to_model_mappings import *


def update_data_in_db(data_entry):
    existing_data = fetch_existing_data_of_person_entry(data_entry)
    return _update_person(existing_data['primary_person'], data_entry)
    # TODO: Spouse
    # TODO: Children


def _update_person(primary_person_model, data_entry):
    return _map_data_to_model(primary_person_model, data_entry, json_to_primary_person)


def _map_data_to_model(model, data_entry, mapping_operations):
    def get_field_from_json(collection, path):
        if len(path) > 0:
            return get_field_from_json(collection[path[0]], path[1:])
        else:
            return collection

    for key, field_details in mapping_operations['mappings'].items():
        result_of_operation = get_field_from_json(data_entry, field_details['json_path'])

        if key in model.get_editable_fields():
            for op in field_details['operations']:
                model, result_of_operation = op(key, model, result_of_operation, data_entry)

    return model
