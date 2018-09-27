import pytest
from datalinking.data_fetcher import KatihaDataFetcher
from datalinking.data_cleaner import KatihaDataCleaner
from datalinking.data_fetcher import MiKARELIADataFetcher
from datalinking.data_cleaner import MiKARELIADataCleaner
from datalinking.data_cleaner import katiha_person_cleaned
from datalinking.data_cleaner import mikarelia_person_cleaned
from tests.datalinking.database.katiha_test_db_utils import KatihaDBUtils
from datalinking.models import katiha_models
from db_management.db_connection import DbConnection
from tests.datalinking.database.katiha_database_test_config import CONFIG
from tests.datalinking.data.mock_katiha_data import MOCK_DATA
from datalinking.utils.duplicate_filter import get_duplicate_filter
from collections import namedtuple


class TestDataFetcher:
    class TestKatihaDataFetcher:
        @pytest.fixture(autouse=True, scope='class', name='katiha_database')
        def katiha_database(self):
            KatihaDBUtils.init_test_db()
            db_connection = DbConnection(db_type='postgres')
            db_connection.init_database(CONFIG['test_db_name'], CONFIG['db_user'], port=CONFIG['db_port'])
            db_connection.connect()
            # Set database of the models
            katiha_models.set_database_to_models(db_connection.get_database())
            return db_connection.get_database()

        @pytest.fixture(autouse=True, scope='class', name='katiha_person_data')
        def populate_person_information_to_db(self, katiha_database):
            KatihaDBUtils.truncate_db()
            # Person data is anonymized and tweaked and only usable for software testing.
            with katiha_database.atomic():
                katiha_models.La.insert_many(MOCK_DATA).execute()
            return MOCK_DATA

        @pytest.fixture(autouse=True, scope='class')
        def fetcher(self):
            cleaner = KatihaDataCleaner()
            return KatihaDataFetcher(cleaner)

        def should_correctly_fetch_cleaned_people_entries(self, katiha_person_data, fetcher):
            people = fetcher.fetch_people()
            assert len(katiha_person_data) == len(people)
            assert type(next(iter(people.values()))) is katiha_person_cleaned

    class TestMiKARELIADataFetcher:
        @pytest.fixture(autouse=True, scope='class')
        def fetcher(self):
            cleaner = MiKARELIADataCleaner()
            return MiKARELIADataFetcher(cleaner)

        def should_correctly_fetch_cleaned_people_entries(self, person_data, fetcher):
            people = fetcher.fetch_people()
            expected_number_of_people = 0
            for person in person_data:
                expected_number_of_people += 1
                if person['spouse'] is not None:
                    expected_number_of_people += 1
            assert len(people) == expected_number_of_people
            assert type(next(iter(people.values()))) is mikarelia_person_cleaned


class TestDuplicateFilter:
    test_nt = namedtuple('TestTuple', 'id name birthyear birthplaces')

    def should_correctly_identify_duplicate_as_such(self):
        find_duplicate = get_duplicate_filter(['name', 'birthyear', 'birthplaces,1'],
                                              identifying_attribute='id')
        mock_data = [self.test_nt(id=1, name='testaaja', birthyear='1950',
                                  birthplaces=['testikylä', 'testikaupunki']),
                     self.test_nt(id=2, name='testaaja', birthyear='1950',
                                  birthplaces=['testikylä', 'testikaupunki', 'lisäkylä'])]

        assert find_duplicate(mock_data[0]) is False
        assert find_duplicate(mock_data[1]) == 1

    def should_not_identify_non_duplicates_as_duplicates(self):
        find_duplicate = get_duplicate_filter(['name', 'birthplaces'], identifying_attribute='id')
        mock_data = [self.test_nt(id=1, name='testaaja', birthyear='1950',
                                  birthplaces=['testikylä', 'salakylä']),
                     self.test_nt(id=2, name='mestaaja', birthyear='1951',
                                  birthplaces=['testikaupunki', 'halikylä'])]

        assert find_duplicate(mock_data[0]) is False
        assert find_duplicate(mock_data[1]) is False
