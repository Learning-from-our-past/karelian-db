import pytest
from tests.utils.dbUtils import DBUtils
import tests.utils.population_utils as population_utils
from models.db_siirtokarjalaistentie_models import *


@pytest.yield_fixture(autouse=True, scope='module', name='person_data')
def populate_person_information_to_db():
    DBUtils.truncate_db()
    return population_utils.populate_from_json("./tests/populate/data/person1.json")[0]


class TestPersonPopulate:
    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    @pytest.yield_fixture(autouse=True, scope='class')
    def spouse(self):
        return Spouse.get()

    def test_person_data_was_populated_correctly(self, person, person_data):
        assert person.firstname == person_data['FirstNames']
        assert person.lastname == person_data['Surname']
        assert person.prevlastname == person_data['OriginalFamily']
        assert person.ownhouse == person_data['Omakotitalo']
        assert person.sex == 'm'
        assert person.returnedkarelia == person_data['ReturnedToKarelia']
        assert person.previousmarriages == person_data['MaybePreviousMarriages']
        assert person.origtext == person_data['originalText']

    def test_dates_were_populated_correctly(self, person, person_data):
        birthdate = Persondate.get(Persondate.id == person.birthdate)
        assert birthdate.day == population_utils.int_or_none(person_data['BirthDay'])
        assert birthdate.month == population_utils.int_or_none(person_data['BirthMonth'])
        assert birthdate.year == population_utils.int_or_none(person_data['BirthYear'])
        assert person.deathdate is None

    def test_profession_was_populated_correctly(self, person, person_data):
        profession = Profession.get(Profession.id == person.profession)
        assert profession.name == person_data['Profession/Status']

    def test_page_was_populated_correctly(self, person, person_data):
        page = Page.get(Page.pagenumber == person.pagenumber)
        assert page.pagenumber == person_data['ApproximatePageNumber']

    def test_living_records_were_populated_correctly(self, person, person_data):
        records = Livingrecord.select().join(Place).where(Livingrecord.person == person.id)

        expected_records2 = person_data['KarelianLocations'] + person_data['OtherLocations']
        assert len(records) == len(expected_records2)

        for i, r in enumerate(records):
            assert r.movedin == population_utils.int_or_none(expected_records2[i]['movedIn'])
            assert r.movedout == population_utils.int_or_none(expected_records2[i]['movedOut'])

            # Json-format is a bit silly. Refactor sometime to make it easier to use...
            if 'KarelianLocation' in expected_records2[i]:
                assert r.place.name == expected_records2[i]['KarelianLocation']
                assert r.place.latitude == expected_records2[i]['KarelianCoordinates']['latitude']
                assert r.place.longitude == expected_records2[i]['KarelianCoordinates']['longitude']
                assert r.place.region == 'karelia'
            else:
                assert r.place.name == expected_records2[i]['OtherLocation']
                assert r.place.latitude == expected_records2[i]['OtherCoordinates']['latitude']
                assert r.place.longitude == expected_records2[i]['OtherCoordinates']['longitude']
                assert r.place.region == 'finland'

    def test_children_were_populated_correctly(self, person, person_data):
        child = (Child.select()
                 .join(Place, on=(Place.id == Child.birthplace))
                 .join(Persondate, on=(Persondate.id == Child.birthdate))
                 .where(Child.parent == person.id))[0]

        # Only one child
        expected_child = person_data['Children'][0]
        assert child.firstname == expected_child['name']
        assert child.lastname == person_data['Surname']
        assert child.sex == 'm'
        assert child.birthdate.year == population_utils.int_or_none(expected_child['birthYear'])

        assert child.birthplace.name == expected_child['locationName']
        assert child.birthplace.latitude == expected_child['childCoordinates']['latitude']
        assert child.birthplace.longitude == expected_child['childCoordinates']['longitude']

    def test_spouse_data_was_populated_correctly(self, spouse, person_data):
        assert spouse.firstname == person_data['Spouse']['SpouseName']
        assert spouse.lastname == person_data['Surname']
        assert spouse.prevlastname == person_data['Spouse']['SpouseOriginalFamily']
        assert spouse.sex == 'f'
        assert spouse.profession.name == person_data['Spouse']['SpouseProfession']
        assert spouse.marriageyear == population_utils.int_or_none(person_data['Spouse']['WeddingYear'])

        assert spouse.birthplace.name == person_data['Spouse']['SpouseBirthData']['BirthLocation']
        assert spouse.birthdate.day == population_utils.int_or_none(person_data['Spouse']['SpouseBirthData']['BirthDay'])
        assert spouse.birthdate.month == population_utils.int_or_none(person_data['Spouse']['SpouseBirthData']['BirthMonth'])
        assert spouse.birthdate.year == population_utils.int_or_none(person_data['Spouse']['SpouseBirthData']['BirthYear'])

        assert spouse.deathdate is None
