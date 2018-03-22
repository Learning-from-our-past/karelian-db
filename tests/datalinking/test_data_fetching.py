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


class TestDataFetcher:
    class TestKatihaDataFetcher:
        @pytest.fixture(autouse=True, scope='class', name='katiha_database')
        def katiha_database(self):
            KatihaDBUtils.init_test_db()
            db_connection = DbConnection(db_type='postgres')
            db_connection.init_database(CONFIG['test_db_name'], CONFIG['db_user'])
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
            assert type(people[0]) is katiha_person_cleaned

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
            assert type(people[0]) is mikarelia_person_cleaned
