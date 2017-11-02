import csv
import os
import shutil

import pytest

import common.database_config as config
from common.testing import population_utils
from common.testing.dbUtils import DBUtils
from database.db_management.csv_record import CsvRecordOfPopulation
from database.db_management.update_database import update_data_in_db


class TestCsvOnUpdateOnExistingDb:

    @pytest.yield_fixture(autouse=True, scope='class', name='person_data')
    def populate_person_information_to_db_anonymized(self, database):  # Override the root populating fixture
        config.CONFIG['anonymize'] = True
        DBUtils.truncate_db()
        return population_utils.populate_from_json(database, "./database/tests/populate/data/person2.json")

    @pytest.yield_fixture(autouse=True)
    def csv_test_dir(self):
        path = './temp/csv'
        if not os.path.exists(path):
            os.makedirs(path)
        yield path

        if os.path.exists(path):
            shutil.rmtree(path)

    def should_create_csv_records_about_sensitive_person_data(self, person_data, csv_test_dir):
        person_models = []

        csv_record = CsvRecordOfPopulation('./temp/csv/test')

        for data_entry in person_data:
            person_models.append(update_data_in_db(data_entry, csv_record))

        csv_record.save_to_file()

        person_details_file = open(csv_test_dir + '/test_persons.csv', 'r', encoding='utf-8')
        person_details = list(csv.DictReader(person_details_file))

        assert person_details[0]['kairaId'] == person_models[0].kairaId
        assert person_details[0]['firstNames'] == 'MIESNIMI'
        assert person_details[0]['lastNames'] == 'MIESSUKUNIMI'
        assert person_details[0]['sourceTextId'] == 'test_1'

        assert person_details[1]['kairaId'] == 'siirtokarjalaiset_1_1S_1'
        assert person_details[1]['firstNames'] == 'VAIMONNIMI'
        assert person_details[1]['lastNames'] == 'MIESSUKUNIMI'
        assert person_details[1]['formerSurname'] == 'VAIMONIMI'
        assert person_details[1]['sourceTextId'] == 'test_1'

        assert person_details[2]['kairaId'] == 'siirtokarjalaiset_1_1C_1'
        assert person_details[2]['firstNames'] == 'Lapsi1'
        assert person_details[2]['lastNames'] == 'MIESSUKUNIMI'
        assert person_details[2]['sourceTextId'] == 'test_1'

        assert person_details[3]['kairaId'] == 'siirtokarjalaiset_1_1C_2'
        assert person_details[3]['firstNames'] == 'Lapsi2'
        assert person_details[3]['lastNames'] == 'MIESSUKUNIMI'
        assert person_details[3]['sourceTextId'] == 'test_1'

        assert person_details[4]['sourceTextId'] == 'test_2'

        source_texts_file = open(csv_test_dir + '/test_source_texts.csv', 'r', encoding='utf-8')
        source_texts = list(csv.DictReader(source_texts_file))

        assert len(source_texts) == 2
        assert source_texts[0]['sourceTextId'] == 'test_1'
        assert source_texts[0]['sourceText'] == 'redacted'
        assert source_texts[1]['sourceTextId'] == 'test_2'
        assert source_texts[1]['sourceText'] == 'redacted2'


class TestCsvOnUpdateOnEmptyDb(TestCsvOnUpdateOnExistingDb):

    @pytest.yield_fixture(autouse=True, scope='function', name='truncate_db')
    def truncate(self):
        DBUtils.truncate_db()

    def should_create_csv_records_about_sensitive_person_data(self, person_data, csv_test_dir):
        person_models = []

        csv_record = CsvRecordOfPopulation('./temp/csv/test')

        for data_entry in person_data:
            person_models.append(update_data_in_db(data_entry, csv_record))

        csv_record.save_to_file()

        person_details_file = open(csv_test_dir + '/test_persons.csv', 'r', encoding='utf-8')
        person_details = list(csv.DictReader(person_details_file))

        assert person_details[0]['kairaId'] == person_models[0].kairaId
        assert person_details[0]['firstNames'] == 'MIESNIMI'
        assert person_details[0]['lastNames'] == 'MIESSUKUNIMI'
        assert person_details[0]['sourceTextId'] == 'test_1'

        assert person_details[1]['kairaId'] == 'siirtokarjalaiset_1_1S_1'
        assert person_details[1]['firstNames'] == 'VAIMONNIMI'
        assert person_details[1]['lastNames'] == 'MIESSUKUNIMI'
        assert person_details[1]['formerSurname'] == 'VAIMONIMI'
        assert person_details[1]['sourceTextId'] == 'test_1'

        assert person_details[2]['kairaId'] == 'siirtokarjalaiset_1_1C_1'
        assert person_details[2]['firstNames'] == 'Lapsi1'
        assert person_details[2]['lastNames'] == 'MIESSUKUNIMI'
        assert person_details[2]['sourceTextId'] == 'test_1'

        assert person_details[3]['kairaId'] == 'siirtokarjalaiset_1_1C_2'
        assert person_details[3]['firstNames'] == 'Lapsi2'
        assert person_details[3]['lastNames'] == 'MIESSUKUNIMI'
        assert person_details[3]['sourceTextId'] == 'test_1'

        assert person_details[4]['sourceTextId'] == 'test_2'

        source_texts_file = open(csv_test_dir + '/test_source_texts.csv', 'r', encoding='utf-8')
        source_texts = list(csv.DictReader(source_texts_file))

        assert len(source_texts) == 2
        assert source_texts[0]['sourceTextId'] == 'test_1'
        assert source_texts[0]['sourceText'] == 'redacted'
        assert source_texts[1]['sourceTextId'] == 'test_2'
        assert source_texts[1]['sourceText'] == 'redacted2'
