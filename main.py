import json
import os
import sys

from csvRecord import CsvRecordOfPopulation
from db_management.models.db_connection import db_connection
from populate import populate_person
from config import CONFIG


def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data

def populate_db(data, csv_record):
    database.set_autocommit(False)
    database.begin()
    with database.atomic():
        for idx, person in enumerate(data):
            populate_person(person, csv_record)
            print("Added ", person['name']['results']["firstNames"], person['name']['results']["surname"], idx+1, '/', len(data))

    database.commit()


    database.set_autocommit(True)
    database.close()


if __name__ == "__main__":
    db_connection.init_database(db_name=CONFIG['db_name'], db_user=CONFIG['db_user'])
    db_connection.connect()
    database = db_connection.get_database()
    csv_record = None

    if len(sys.argv) > 1:
        file_name = os.path.splitext(sys.argv[1])[0]
        csv_record = CsvRecordOfPopulation(file_name)
        data = load_json(sys.argv[1])
    else:
        data = load_json("./material/testset.json")
        csv_record = CsvRecordOfPopulation('./material/testset')

    populate_db(data, csv_record)
    csv_record.save_to_file()


