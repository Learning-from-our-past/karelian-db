import argparse
import json
import os
import sys
import pickle

import db_management.siirtokarjalaistentie_models as db_siirtokarjalaistentie_models
from db_management import katiha_models
from db_management import divaevi_models
from db_management.database_config import CONFIG
from db_management.db_connection import db_connection
from db_management.csv_record import CsvRecordOfPopulation
from db_management.mark_ambiguous_region_places_in_db import mark_ambiguous_places
from db_management.update_database import update_data_in_db
from db_management.update_report import update_report
from datalinking.data_populater import populate_linked_data
from datalinking.divaevi_populater import populate_linked_data as divaevi_populate

parser = argparse.ArgumentParser(description='Populate data to the database from json files.')
parser.add_argument('-a', nargs='?', type=str, help='Host address to the database', default='localhost')
parser.add_argument('-p', nargs='?', type=int, help='Port of the database', default=CONFIG['db_port'])
parser.add_argument('-u', nargs='?', type=str, help='User name. Password should be stored in pgpassfile', default=CONFIG['db_user'])
parser.add_argument('-d', nargs='?', type=str, help='Database name', default=CONFIG['db_name'])
parser.add_argument('-t', nargs=1, type=str, help='Data type to populate')
parser.add_argument('file', metavar='file', type=str, nargs=1, help='The file to populate data from')

def load_json(path):
    with open(path, encoding='utf8') as data_file:
        data = json.load(data_file)
    return data

def load_pickle(path):
    with open(path, mode='rb') as data_file:
        data = pickle.load(data_file)
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
    print('Target:', args['a'], args['d'], args['p'])

    db_connection.init_database(db_name=args['d'], db_user=args['u'], host=args['a'], port=args['p'])
    db_connection.connect()
    database = db_connection.get_database()

    # Set database of the models
    db_siirtokarjalaistentie_models.set_database_to_models(database)
    katiha_models.set_database_to_models(database)
    divaevi_models.set_database_to_models(database)

    data_type = args['t'][0].casefold()
    file_name = os.path.splitext(args['file'][0])[0]
    update_report.setup(file_name)

    if data_type == 'kaira':
        csv_record = CsvRecordOfPopulation(file_name)
        data = load_json(args['file'][0])
        populate_db(database, data, csv_record)
        csv_record.save_to_file()
    elif data_type == 'katiha':
        data = load_pickle(args['file'][0])
        populate_linked_data(database, data)
    elif data_type == 'divaevi':
        data = load_pickle(args['file'][0])
        divaevi_populate(database,data)
