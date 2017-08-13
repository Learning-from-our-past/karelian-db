import json
from db_management.update_database import update_data_in_db


class MockRecord:

    def add_primary_person(self, person):
        pass

    def add_child(self, primary_person, child):
        pass

    def add_spouse(self, primary_person, spouse):
        pass

    def save_to_file(self):
        pass

def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data


def populate_from_json(path):
    data = load_json(path)

    for idx, person in enumerate(data):
        update_data_in_db(person, MockRecord())

    return data

def int_or_none(value):
    try:
        return int(value)
    except TypeError:
        return None