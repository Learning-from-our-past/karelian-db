from db_management.fetch_existing_data import fetch_existing_data_of_person_entry
from db_management.json_to_model_mappings import *


def update_data_in_db(data_entry):
    existing_data = fetch_existing_data_of_person_entry(data_entry)

    primary_person = _update_person(existing_data['primary_person'], data_entry)

    spouse_person = None
    if data_entry['spouse']['hasSpouse']:
        spouse_person = _update_spouse(existing_data['spouse_person'], primary_person, data_entry)

    _update_children(existing_data['children'], primary_person, spouse_person, data_entry)

    return primary_person


def _update_person(primary_person_model, data_entry):
    person = _map_data_to_model(primary_person_model, data_entry, json_to_primary_person)
    person.save()

    _map_data_to_one_to_many_models(person, data_entry, json_to_primary_person)

    return person


def _update_spouse(spouse_person_model, primary_person_model, data_entry):
    spouse_person = _map_data_to_model(spouse_person_model, data_entry, json_to_spouse)
    spouse_person.save()

    _map_data_to_one_to_many_models({'main': spouse_person_model, 'primary': primary_person_model}, data_entry, json_to_spouse)

    return spouse_person


def _update_children(children_models, primary_person_model, spouse_person_model, data_entry):
    for idx, child in enumerate(children_models):
        _map_data_to_model(child, data_entry, json_to_child, {'primary_person': primary_person_model, 'spouse': spouse_person_model}, index=idx)
        child.save()

    return children_models


def _get_field_from_json(collection, path, index):
    if len(path) > 0:
        # Allow to iterate over list based on given index. Note that this works now only on
        # one level since same index is passed forward but that is fine for now since this is used to
        # iterate over json's root level lists such children.
        if path[0] == '*' and type(collection) is list:
            return _get_field_from_json(collection[index], path[1:], index)

        return _get_field_from_json(collection[path[0]], path[1:], index)
    else:
        return collection


def _map_data_to_model(model, other_models, mapping_operations, extra_data=None, index=None):

    for key, field_details in mapping_operations['mappings'].items():
        result_of_operation = _get_field_from_json(other_models, field_details['json_path'], index)

        if model.get_editable_fields() is None or key in model.get_editable_fields():
            for op in field_details['operations']:
                model, result_of_operation = op(key, model, result_of_operation, other_models, extra_data)

    return model


def _map_data_to_one_to_many_models(models, data_entry, mapping_operations, extra_data=None, index=None):
    if extra_data is None:
        extra_data = {}

    for key, field_details in mapping_operations['one_to_many'].items():
        result_of_operation = _get_field_from_json(data_entry, field_details['json_path'], index)

        for op in field_details['operations']:
            models, result_of_operation = op(key, models, result_of_operation, data_entry, extra_data)

    return models
