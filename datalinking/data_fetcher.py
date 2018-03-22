from abc import abstractmethod
from abc import ABC
from datalinking.models import katiha_models
from db_management import siirtokarjalaistentie_models as mikarelia_models
from tqdm import tqdm


class DataFetcher(ABC):
    def __init__(self, data_cleaner):
        self._data_cleaner = data_cleaner

    @abstractmethod
    def fetch_people(self):
        pass


class KatihaDataFetcher(DataFetcher):
    def fetch_people(self):
        la_person = katiha_models.La

        people_results = la_person.select(
            la_person.id, la_person.eventId, la_person.firstName, la_person.secondName,
            la_person.lastName, la_person.birthParish, la_person.birthDay, la_person.birthMonth,
            la_person.birthYear, la_person.parishId, la_person.motherLanguage
        ).where(
            la_person.birthYear.between(1870, 1970) &
            la_person.firstName.is_null(False) &
            la_person.lastName.is_null(False)
        ).tuples().execute()

        people = []
        for row in tqdm(people_results):
            people.append(self._data_cleaner(row))

        return people


class MiKARELIADataFetcher(DataFetcher):
    def fetch_people(self):
        person = mikarelia_models.Person
        place = mikarelia_models.Place
        people_results = person.select(
            person.kairaId, person.firstName, person.lastName, person.formerSurname,
            person.sex, place.name, person.birthDay, person.birthMonth, person.birthYear
        ).join(place).tuples().execute()

        people = []
        for row in tqdm(people_results):
            people.append(self._data_cleaner(row))
        return people
