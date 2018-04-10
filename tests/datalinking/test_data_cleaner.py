import pytest
from collections import OrderedDict
from datalinking.data_cleaner import KatihaDataCleaner
from datalinking.data_cleaner import katiha_person_cleaned


class TestKatihaDataCleaner:
    @pytest.fixture(autouse=True, scope='class')
    def cleaner(self):
        return KatihaDataCleaner()

    @pytest.fixture(autouse=True, scope='class')
    def data(self):
        # This data is completely made up, but it has to look real (i.e. names and parish id)
        # so that the table lookups and name normalizations
        d = OrderedDict()
        d['ID'] = 1
        d['eventId'] = '0504L024b0000431'
        d['firstName'] = 'Tuomas           '
        d['secondName'] = 'Juuso               '
        d['lastName'] = 'Salmi                       '
        d['birthParish'] = '                              '
        d['birthDay'] = 20
        d['birthMonth'] = 5
        d['birthYear'] = 1930
        d['parishId'] = '0504'
        d['motherLanguage'] = ' '
        return d

    def should_correctly_return_cleaned_person_object(self, cleaner, data):
        expected_data = katiha_person_cleaned(db_id=data['ID'],
                                              event_ids=(data['eventId'],),
                                              normalized_first_names=('thomas', 'joseph'),
                                              normalized_last_name='salmen',
                                              date_of_birth=(data['birthDay'], data['birthMonth'], data['birthYear']))
        cleaned_data = cleaner.clean_db_rows(data.values())
        assert cleaned_data == expected_data
