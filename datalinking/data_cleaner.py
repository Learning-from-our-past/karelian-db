from abc import ABC, abstractmethod
from datalinking.historical_name_normalizer.name_normalizer import NameNormalizer
from datalinking.support_data.place_names import GENERALIZE_MIKARELIA_BIRTHPLACE
from datalinking.utils.name_utils import find_former_lastnames
from datalinking.utils.code_enumerations import *
from itertools import chain
from functools import lru_cache
from functools import partial
from collections import namedtuple
from datalinking.utils.resolve_birthplace import resolve_birthplace_to_mikarelia_birthplace
from db_management.testing.population_utils import int_or_none

# FIXME: These need to be updated if we want to add more data to fetch from katiha in datalinking
katiha_person_raw = namedtuple('KatihaPersonRaw',
                               ('ID eventId firstName secondName lastName birthParish '
                                'birthDay birthMonth birthYear parishId motherLanguage sex '
                                'birthInMarriage multipleBirth'))
katiha_person_cleaned = namedtuple('KatihaPersonCleaned',
                                   ('db_id event_ids normalized_first_names normalized_last_name '
                                    'date_of_birth birthplace mother_language sex birth_in_marriage '
                                    'multiple_birth'))


class DataCleaner(ABC):
    def __init__(self):
        fname_normalize = NameNormalizer('first').normalize
        self._normalize_first_name = partial(fname_normalize, find_nearest=False)
        lname_normalize = NameNormalizer('last').normalize
        self._normalize_last_name = partial(lname_normalize, find_nearest=False)

    def __call__(self, *args, **kwargs):
        return self.clean_db_rows(*args, **kwargs)

    @abstractmethod
    def clean_db_rows(self, data):
        pass

    @lru_cache(maxsize=None)
    def _get_normalized_first_name(self, name):
        return self._normalize_first_name(name)

    @lru_cache(maxsize=None)
    def _get_normalized_last_name(self, name):
        return self._normalize_last_name(name)


class KatihaDataCleaner(DataCleaner):
    def __init__(self):
        super().__init__()
        self._mother_language_map = {0: 'other', 1: 'finnish', 2: 'swedish',
                                     3: 'russian', 4: 'german'}
        self._sex_map = {1: 'm', 2: 'f'}
        self._birth_in_marriage_map = get_code_map(BirthInMarriageCodes)

    def clean_db_rows(self, row):
        """
        Cleans the person data (row from database) into a format ready for data linking.
        :param row: A tuple containing the rows returned by the DB query
        :return: namedtuple('KatihaPersonCleaned')
        """
        person_raw = katiha_person_raw(*row)
        norm_first_names = self._find_first_names_of_person(person_raw)
        norm_last_name = self._find_last_name_in_string(person_raw.lastName)
        dob = (person_raw.birthDay, person_raw.birthMonth, person_raw.birthYear)
        mk_birthplace = resolve_birthplace_to_mikarelia_birthplace(person_raw)
        person_cleaned = katiha_person_cleaned(
            db_id=person_raw.ID,
            normalized_first_names=norm_first_names,
            normalized_last_name=norm_last_name,
            event_ids={person_raw.eventId},
            date_of_birth=dob,
            birthplace=mk_birthplace,
            mother_language=self._resolve_mother_language(person_raw.motherLanguage),
            sex=self._sex_map.get(int_or_none(person_raw.sex), None),
            birth_in_marriage=self._resolve_birth_in_marriage(person_raw.birthInMarriage),
            multiple_birth=int_or_none(person_raw.multipleBirth)
        )
        return person_cleaned

    def _find_first_names_of_person(self, person):
        """
        Normalizes a katiha person's first names using Eric Malmi's NameNormalizer
        :param person: A namedtuple('KatihaPersonRaw')
        :return: A tuple of the person's normalized names
        """
        names = (name for name in person.firstName.split(' ')
                 if name)
        if person.secondName:
            names = chain(
                names,
                (name for name in person.secondName.split(' ')
                 if name)
            )
        return tuple(self._get_normalized_first_name(name) for name in names if len(name) > 2)

    def _find_last_name_in_string(self, last_names):
        """
        Normalizes a katiha person's last name using Eric Malmi's NameNormalizer
        :param last_names: A last name string from Katiha
        :return: A string, the first last name if there are multiple, normalized
        """
        names = (name for name in last_names.strip().split(' '))
        name = next(names)
        if name and len(name) >= 2:
            return self._get_normalized_last_name(name)
        else:
            return None

    def _resolve_mother_language(self, mother_language_identifier):
        mother_language = int_or_none(mother_language_identifier)
        if mother_language is not None:
            mother_language = self._mother_language_map[mother_language]
        return mother_language

    def _resolve_birth_in_marriage(self, birth_in_marriage_code):
        return self._birth_in_marriage_map.get(int_or_none(birth_in_marriage_code), None)


mikarelia_person_raw = namedtuple('MikareliaPersonRaw',
                                  ('kairaId firstName lastName formerSurname sex birthPlace '
                                   'birthDay birthMonth birthYear'))
mikarelia_person_cleaned = namedtuple('MikareliaPersonCleaned',
                                      ('db_id normalized_first_names normalized_last_name '
                                       'date_of_birth birthplace'))


class MiKARELIADataCleaner(DataCleaner):
    def __init__(self):
        super().__init__()

    def clean_db_rows(self, row):
        """
        Cleans the person data (row from database) into a format ready for data linking.
        :param row: A tuple containing the rows returned by the DB query
        :return: namedtuple('MiKARELIAPersonCleaned')
        """
        person_raw = mikarelia_person_raw(*row)
        norm_first_names = self._find_normalized_first_names_from_string(person_raw.firstName)
        norm_last_name = self._find_normalized_last_name(person_raw)
        dob = (person_raw.birthDay, person_raw.birthMonth, person_raw.birthYear)
        person_cleaned = mikarelia_person_cleaned(
            db_id=person_raw.kairaId,
            normalized_first_names=norm_first_names,
            normalized_last_name=norm_last_name,
            date_of_birth=dob,
            birthplace=self._clean_birthplace(person_raw.birthPlace),
        )
        return person_cleaned

    def _find_normalized_first_names_from_string(self, first_name):
        """
        Normalizes a MiKARELIA person's first names using normalized name maps generated with
        one of the invoke tasks.
        :param first_name: A first name string from MiKARELIA
        :return: A tuple of the person's normalized names
        """
        names = (name for name in first_name.split(' ') if name)
        return tuple(self._get_normalized_first_name(name) for name in names if len(name) >= 2)

    def _find_normalized_last_name(self, person):
        """
        Normalizes a MiKARELIA person's last name using normalized name maps generated with
        one of the invoke tasks.
        :param person: A namedtuple('MiKARELIAPersonRaw')
        :return: A tuple of the person's normalized names
        """

        # If the person is female, we use their first former surname (which, in MiKARELIA, is
        # their maiden name. Women are recorded in the Katiha data with their maiden names.
        last_names = None
        if person.sex == 'f' and person.formerSurname:
            last_names = find_former_lastnames(person.formerSurname)
        elif (person.sex == 'm' or not person.formerSurname) and person.lastName:
            last_names = [name for name in person.lastName.strip().split(' ') if len(name) >= 2]

        if not last_names:
            return None

        return self._get_normalized_last_name(last_names[0])

    def _clean_birthplace(self, birthplace):
        birthplace = birthplace.casefold().replace('-', '').replace(' ', '')
        if birthplace in GENERALIZE_MIKARELIA_BIRTHPLACE:
            birthplace = GENERALIZE_MIKARELIA_BIRTHPLACE[birthplace]
        return birthplace
