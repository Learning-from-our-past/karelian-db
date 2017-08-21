import json
import os
import sys

from config import CONFIG
from db_management.csvRecord import CsvRecordOfPopulation
from db_management.models.db_connection import db_connection
from db_management.update_database import update_data_in_db
from db_management.update_report import update_report


def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data


def print_progress(current, max):
    percentage = round((current / max) * 100)
    sys.stdout.write("Progress: %d%% - %d/%d   \r" % (percentage, current, max))
    sys.stdout.flush()

def populate_db(data, csv_record):
    print('Populating data...')
    database.set_autocommit(False)
    database.begin()

    database.execute_sql("""
    LOCK TABLE siirtokarjalaisten_tie."Person" IN SHARE ROW EXCLUSIVE MODE;
    LOCK TABLE siirtokarjalaisten_tie."Child" IN SHARE ROW EXCLUSIVE MODE;
    LOCK TABLE siirtokarjalaisten_tie."LivingRecord" IN SHARE ROW EXCLUSIVE MODE;
    LOCK TABLE siirtokarjalaisten_tie."Marriage" IN SHARE ROW EXCLUSIVE MODE;
    LOCK TABLE siirtokarjalaisten_tie."Page" IN SHARE ROW EXCLUSIVE MODE;
    LOCK TABLE siirtokarjalaisten_tie."Place" IN SHARE ROW EXCLUSIVE MODE;
    LOCK TABLE siirtokarjalaisten_tie."Profession" IN SHARE ROW EXCLUSIVE MODE;
    """)

    with database.atomic():
        for idx, person in enumerate(data):
            update_data_in_db(person, csv_record)
            print_progress(idx, len(data))

    update_report.save_report()
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
        update_report.setup(file_name)
        csv_record = CsvRecordOfPopulation(file_name)
        data = load_json(sys.argv[1])
    else:
        data = load_json("./material/testset.json")
        csv_record = CsvRecordOfPopulation('./material/testset')

    populate_db(data, csv_record)
    csv_record.save_to_file()


