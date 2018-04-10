from abc import ABC, abstractmethod
from datalinking.historical_name_normalizer.name_normalizer import NameNormalizer
from itertools import chain
from functools import lru_cache
from functools import partial
from collections import namedtuple

# FIXME: These need to be updated if we want to add more data to fetch from katiha in datalinking
katiha_person_raw = namedtuple('KatihaPersonRaw',
                               ('ID eventId firstName secondName lastName birthParish '
                                'birthDay birthMonth birthYear parishId motherLanguage'))
katiha_person_cleaned = namedtuple('KatihaPersonCleaned',
                                   ('db_id event_ids normalized_first_names normalized_last_name '
                                    'date_of_birth'))


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
        person_cleaned = katiha_person_cleaned(db_id=person_raw.ID,
                                               normalized_first_names=norm_first_names,
                                               normalized_last_name=norm_last_name,
                                               event_ids=(person_raw.eventId,),
                                               date_of_birth=dob)
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
