import pytest
from collections import OrderedDict
from datalinking.data_cleaner import KatihaDataCleaner
from datalinking.data_cleaner import katiha_person_cleaned
from datalinking.utils.resolve_birthplace import resolve_birthplace_to_mikarelia_birthplace
from datalinking.data_cleaner import katiha_person_raw
from datalinking.data_cleaner import MiKARELIADataCleaner
from datalinking.data_cleaner import mikarelia_person_cleaned


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
        d['motherLanguage'] = '1'
        d['sex'] = 1
        d['birthInMarriage'] = '2'
        d['multipleBirth'] = 3
        d['vaccination'] = '3'
        d['literate'] = 1
        d['departureType'] = 2
        d['departureDay'] = 21
        d['departureMonth'] = 5
        d['departureYear'] = 1930
        return d

    def should_correctly_return_cleaned_person_object(self, cleaner, data):
        expected_data = katiha_person_cleaned(db_id=data['ID'],
                                              event_ids={data['eventId']},
                                              normalized_first_names=('thomas', 'joseph'),
                                              normalized_last_name='salmen',
                                              birthplace='sortavala',
                                              date_of_birth=(data['birthDay'], data['birthMonth'], data['birthYear']),
                                              mother_language='finnish',
                                              sex='m',
                                              birth_in_marriage='born out of wedlock',
                                              multiple_birth=3,
                                              vaccinated=True,
                                              rokko=True,
                                              literate=True,
                                              literacy_confirmed=False,
                                              departure_type='died',
                                              departure_date=(data['departureDay'], data['departureMonth'], data['departureYear']))
        cleaned_data = cleaner.clean_db_rows(data.values())
        assert cleaned_data == expected_data

    class TestBirthplaceResolver:
        def should_correctly_convert_parish_id_to_birthplace(self, data):
            p = katiha_person_raw(**data)
            cleaned_birthplace = resolve_birthplace_to_mikarelia_birthplace(p)
            assert cleaned_birthplace == 'sortavala'

        def should_correctly_handle_situation_when_birth_parish_is_here(self, data):
            # in the situation when birthParish is "täällä" (the Finnish word for "here"),
            # we want to use the value of parishId instead
            data['birthParish'] = 'täällä'
            p = katiha_person_raw(**data)
            cleaned_birthplace = resolve_birthplace_to_mikarelia_birthplace(p)
            assert cleaned_birthplace == 'sortavala'

        def should_correctly_use_birth_parish_instead_of_parish_id_if_available(self, data):
            # The database row can have both a birthParish column with a value and a parishId
            # column with a value. Usually this means that the person was born in a different
            # Parish (=birthParish) than in whose parish's book they are (=parishId). In these
            # cases we want to use birthParish instead.
            data['birthParish'] = '  impi-lahti  '
            p = katiha_person_raw(**data)
            cleaned_birthplace = resolve_birthplace_to_mikarelia_birthplace(p)
            assert cleaned_birthplace == 'impilahti'

        def should_correctly_fix_alternate_form_of_birth_parish_name_to_be_mikarelia_compatible(self, data):
            data['birthParish'] = 'j.'
            p = katiha_person_raw(**data)
            cleaned_birthplace = resolve_birthplace_to_mikarelia_birthplace(p)
            assert cleaned_birthplace == 'viipuri'


class TestMiKARELIADataCleaner:
    @pytest.fixture(autouse=True, scope='class')
    def cleaner(self):
        return MiKARELIADataCleaner()

    @pytest.fixture(autouse=True, scope='function')
    def data(self):
        # This data is completely made up, but it has to look real (i.e. names and parish id)
        # so that the table lookups work
        d = OrderedDict()
        d['kairaId'] = 'siirtokarjalaiset_1_42S_1'
        d['firstName'] = 'Tuomas Juuso'
        d['lastName'] = 'Salmi'
        d['formerSurname'] = 'Rallikuski'
        d['sex'] = 'm'
        d['birthPlace'] = 'Käkisalmenmlk'
        d['birthDay'] = 11
        d['birthMonth'] = 6
        d['birthYear'] = 1921
        return d

    def should_correctly_return_cleaned_person_object(self, cleaner, data):
        expected_data = mikarelia_person_cleaned(
            db_id=data['kairaId'],
            date_of_birth=(data['birthDay'], data['birthMonth'], data['birthYear']),
            birthplace='käkisalmi',
            normalized_first_names=('thomas', 'joseph'),
            normalized_last_name='salmen'
        )
        assert expected_data == cleaner.clean_db_rows(data.values())
