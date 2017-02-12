import json
from populate import populate_person


def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data


def populate_from_json(path):
    data = load_json(path)

    for idx, person in enumerate(data):
        populate_person(person)

    return data

def int_or_none(value):
    try:
        return int(value)
    except TypeError:
        return None