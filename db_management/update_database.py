from db_management.fetch_existing_data import fetch_existing_data_of_person_entry
from db_management.json_to_model_mappings import *
from db_management.exceptions import *


def update_data_in_db(data_entry, csv_record):
    existing_data = fetch_existing_data_of_person_entry(data_entry)

    primary_person = _update_person(existing_data['primary_person'], data_entry, csv_record)

    spouse_person = None
    if data_entry['spouse']['hasSpouse']:
        spouse_person = _update_spouse(existing_data['spouse_person'], primary_person, data_entry, csv_record)

    _update_children(primary_person, spouse_person, data_entry, csv_record)

    return primary_person


def _update_person(primary_person_model, data_entry, csv_record):
    person = _map_data_to_model(primary_person_model, data_entry, json_to_primary_person)
    person.sourceTextId = csv_record.add_primary_person(data_entry)
    person.save()

    _map_data_to_one_to_many_models(person, data_entry, json_to_primary_person)

    return person


def _update_spouse(spouse_person_model, primary_person_model, data_entry, csv_record):
    spouse_person = _map_data_to_model(spouse_person_model, data_entry, json_to_spouse)
    spouse_person.sourceTextId = csv_record.add_spouse(data_entry, data_entry['spouse'])
    spouse_person.save()

    _map_data_to_one_to_many_models({'main': spouse_person_model, 'primary': primary_person_model}, data_entry, json_to_spouse)

    return spouse_person


def _update_children(primary_person_model, spouse_person_model, data_entry, csv_record):
    try:
        # Preprocess will update data entries and it will return a set of models to be used in population
        children_models, data_entry = _preprocess_data(data_entry, mapping_operations=json_to_child, extra_data={'primary_person': primary_person_model, 'spouse': spouse_person_model})

        for idx, child in enumerate(children_models):
            _map_data_to_model(child, data_entry, json_to_child, extra_data={'primary_person': primary_person_model, 'spouse': spouse_person_model}, index=idx)
            child.sourceTextId = csv_record.add_child(data_entry, data_entry['children'][idx])

            child.save()
    except DataEntryValidationException:
        # Children was not updated. Either there were no changes or some of the children were edited manually

        # Children should still be in csv
        for child in data_entry['children']:
            csv_record.add_child(data_entry, child)

        children_models = []

    return children_models


def _get_field_from_json(collection, path, index=0):
    if len(path) > 0:
        # Allow to iterate over list based on given index. Note that this works now only on
        # one level since same index is passed forward but that is fine for now since this is used to
        # iterate over json's root level lists such children.
        if path[0] == '*' and type(collection) is list:
            return _get_field_from_json(collection[index], path[1:], index)

        return _get_field_from_json(collection[path[0]], path[1:], index)
    else:
        return collection


def _preprocess_data(data_entry, mapping_operations, extra_data):
    # Mutate data and run other operations for the datastructure before it is handed to the field operations
    preprocess_target = _get_field_from_json(data_entry, mapping_operations['preprocess_operations']['json_path'])
    models = []

    if mapping_operations['preprocess_operations']['operation'] is not None:
        models, preprocess_target = mapping_operations['preprocess_operations']['operation'](preprocess_target, data_entry, extra_data)
    return models, data_entry


def _map_data_to_model(model, data_entry, mapping_operations, extra_data=None, index=None):

    for key, field_details in mapping_operations['mappings'].items():
        result_of_operation = _get_field_from_json(data_entry, field_details['json_path'], index)

        if model.get_editable_fields() is None or key in model.get_editable_fields():
            for op in field_details['operations']:
                model, result_of_operation = op(key, model, result_of_operation, data_entry, extra_data)

    return model


def _map_data_to_one_to_many_models(models, data_entry, mapping_operations, extra_data=None, index=None):
    if extra_data is None:
        extra_data = {}

    for key, field_details in mapping_operations['one_to_many'].items():
        result_of_operation = _get_field_from_json(data_entry, field_details['json_path'], index)

        for op in field_details['operations']:
            models, result_of_operation = op(key, models, result_of_operation, data_entry, extra_data)

    return models
