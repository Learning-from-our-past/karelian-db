from abc import abstractmethod
from abc import ABC
from datalinking.models import katiha_models
from db_management import siirtokarjalaistentie_models as mikarelia_models
from datalinking.utils.data_collaters import get_frequency_collater
from datalinking.utils.duplicate_filter import get_duplicate_filter
from datalinking.data_cleaner import katiha_person_cleaned
from tqdm import tqdm


class DataFetcher(ABC):
    def __init__(self, data_cleaner):
        self._data_cleaner = data_cleaner

    @abstractmethod
    def fetch_people(self):
        pass


class KatihaDataFetcher(DataFetcher):
    def fetch_people(self):
        people_data = self._get_data()
        return self._get_people_without_duplicates(people_data)

    @staticmethod
    def _get_data():
        la_person = katiha_models.La

        people_results = la_person.select(
            la_person.id, la_person.eventId, la_person.firstName, la_person.secondName,
            la_person.lastName, la_person.birthParish, la_person.birthDay, la_person.birthMonth,
            la_person.birthYear, la_person.parishId, la_person.motherLanguage, la_person.sex,
            la_person.birthInMarriage
        ).where(
            la_person.birthYear.between(1870, 1970) &
            la_person.firstName.is_null(False) &
            la_person.lastName.is_null(False)
        ).tuples().execute()
        return people_results

    def _get_people_without_duplicates(self, data):
        find_duplicate = get_duplicate_filter(['date_of_birth', 'normalized_last_name',
                                               'birthplace', 'normalized_first_names,0'],
                                              identifying_attribute='db_id')
        people = {}

        for row in tqdm(data):
            person = self._data_cleaner(row)
            if len(person.normalized_first_names) > 0 and person.normalized_last_name:
                unique_key = find_duplicate(person)
                if unique_key:
                    people[unique_key] = self._collate_data(people[unique_key], person)
                else:
                    people[person.db_id] = person
        return people

    @staticmethod
    def _collate_data(primary, duplicate):
        """
        Collates data under the primary person "entry" when encountering duplicates. Doing this
        we can get as much data as possible, and it's also essential to combine everyone's eventIds
        to get the family data properly.
        :param primary: katiha_person_cleaned namedtuple - the primary person entry under which we
        collate the data
        :param duplicate: katiha_person_cleaned namedtuple - duplicate that was found for primary
        :return: katiha_person_cleaned namedtuple - new entry with primary and duplicate data
        collated
        """
        collaters = [get_frequency_collater('mother_language'),
                     get_frequency_collater('sex'),
                     get_frequency_collater('birth_in_marriage')]

        collated_attributes = [{'event_ids': primary.event_ids | duplicate.event_ids}]
        for collater in collaters:
            collated_attributes.append(collater(primary.db_id, duplicate))

        collated_dict = primary._asdict()
        for attribute in collated_attributes:
            collated_dict.update(attribute)
        collated_data = katiha_person_cleaned(**collated_dict)
        return collated_data


class MiKARELIADataFetcher(DataFetcher):
    def fetch_people(self):
        people_data = self._get_data()

        people = {}
        for row in tqdm(people_data):
            person = self._data_cleaner(row)
            if len(person.normalized_first_names) > 0 and person.normalized_last_name:
                people[person.db_id] = person
        return people

    @staticmethod
    def _get_data():
        person = mikarelia_models.Person
        place = mikarelia_models.Place
        people_results = person.select(
            person.kairaId, person.firstName, person.lastName, person.formerSurname,
            person.sex, place.name, person.birthDay, person.birthMonth, person.birthYear
        ).join(place).tuples().execute()
        return people_results
