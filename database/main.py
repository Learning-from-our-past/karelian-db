import argparse
import json
import os
import sys

import common.siirtokarjalaistentie_models as db_siirtokarjalaistentie_models
from common.db_connection import db_connection
from database.config import CONFIG
from database.db_management.csvRecord import CsvRecordOfPopulation
from database.db_management.mark_ambiguous_region_places_in_db import mark_ambiguous_places
from database.db_management.update_database import update_data_in_db
from database.db_management.update_report import update_report

parser = argparse.ArgumentParser(description='Populate data to the database from json files.')
parser.add_argument('-a', nargs='?', type=str, help='Host address to the database', default='localhost')
parser.add_argument('-p', nargs='?', type=int, help='Port of the database', default=5432)
parser.add_argument('-u', nargs='?', type=str, help='User name. Password should be stored in pgpassfile', default=CONFIG['db_user'])
parser.add_argument('-d', nargs='?', type=str, help='Database name', default=CONFIG['db_name'])
parser.add_argument('file', metavar='file', type=str, nargs=1, help='The file to populate data from')

def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data


def print_progress(current, max):
    percentage = round((current / max) * 100)
    sys.stdout.write("Progress: %d%% - %d/%d   \r" % (percentage, current, max))
    sys.stdout.flush()

def populate_db(database, data, csv_record):
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

    mark_ambiguous_places(database)

    database.set_autocommit(True)
    database.close()


if __name__ == "__main__":
    args = vars(parser.parse_args())
    print('Target:', args['a'], args['d'])

    db_connection.init_database(db_name=args['d'], db_user=args['u'], host=args['a'], port=args['p'])
    db_connection.connect()
    database = db_connection.get_database()

    # Set database of the models
    db_siirtokarjalaistentie_models.set_database_to_models(database)

    csv_record = None

    if len(sys.argv) > 1:
        file_name = os.path.splitext(sys.argv[1])[0]
        update_report.setup(file_name)
        csv_record = CsvRecordOfPopulation(file_name)
        data = load_json(sys.argv[1])
    else:
        data = load_json("./material/testset.json")
        csv_record = CsvRecordOfPopulation('./material/testset')

    populate_db(database, data, csv_record)
    csv_record.save_to_file()


