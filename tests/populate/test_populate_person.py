import pytest
from tests.utils.dbUtils import DBUtils
import tests.utils.population_utils as population_utils
from models.db_siirtokarjalaistentie_models import *


@pytest.yield_fixture(autouse=True, scope='module', name='person_data')
def populate_person_information_to_db():
    DBUtils.truncate_db()
    # Person data is anonymized and tweaked and only usable for software testing.
    return population_utils.populate_from_json("./tests/populate/data/person1.json")[0]


class TestPersonPopulate:
    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    @pytest.yield_fixture(autouse=True, scope='class')
    def spouse(self):
        return Spouse.get()

    def test_person_data_was_populated_correctly(self, person, person_data):
        assert person.firstname == person_data['firstNames']
        assert person.lastname == person_data['surname']
        assert person.prevlastname == person_data['originalFamily']
        assert person.ownhouse == person_data['omakotitalo']
        assert person.sex == 'm'
        assert person.returnedkarelia == person_data['returnedToKarelia']
        assert person.previousmarriages == person_data['maybePreviousMarriages']
        assert person.origtext == person_data['originalText']

    def test_dates_were_populated_correctly(self, person, person_data):
        birthdate = Persondate.get(Persondate.id == person.birthdate)
        assert birthdate.day == population_utils.int_or_none(person_data['birthDay'])
        assert birthdate.month == population_utils.int_or_none(person_data['birthMonth'])
        assert birthdate.year == population_utils.int_or_none(person_data['birthYear'])
        assert person.deathdate is None

    def test_profession_was_populated_correctly(self, person, person_data):
        profession = Profession.get(Profession.id == person.profession)
        assert profession.name == person_data['profession']

    def test_page_was_populated_correctly(self, person, person_data):
        page = Page.get(Page.pagenumber == person.pagenumber)
        assert page.pagenumber == person_data['approximatePageNumber']

    def test_living_records_were_populated_correctly(self, person, person_data):
        records = sorted(Livingrecord.select().join(Place).where(Livingrecord.person == person.id), key = lambda x: (x.movedin is None, x.movedin))

        expected_records = sorted(person_data['locations'], key = lambda x: (x['movedIn'] is None, x['movedIn']))
        assert len(records) == len(expected_records)

        for i, r in enumerate(records):
            assert r.movedin == population_utils.int_or_none(expected_records[i]['movedIn'])
            assert r.movedout == population_utils.int_or_none(expected_records[i]['movedOut'])

            assert r.place.name == expected_records[i]['locationName']
            assert r.place.latitude == expected_records[i]['coordinates']['latitude']
            assert r.place.longitude == expected_records[i]['coordinates']['longitude']
            assert r.place.region == expected_records[i]['region']

    def test_children_were_populated_correctly(self, person, person_data):
        child = (Child.select()
                 .join(Place, on=(Place.id == Child.birthplace))
                 .join(Persondate, on=(Persondate.id == Child.birthdate))
                 .where(Child.parent == person.id))[0]

        # Only one child
        expected_child = person_data['children'][0]
        assert child.firstname == expected_child['name']
        assert child.lastname == person_data['surname']
        assert child.sex == 'm'
        assert child.birthdate.year == population_utils.int_or_none(expected_child['birthYear'])

        assert child.birthplace.name == expected_child['location']
        assert child.birthplace.latitude == expected_child['coordinates']['latitude']
        assert child.birthplace.longitude == expected_child['coordinates']['longitude']

    def test_spouse_data_was_populated_correctly(self, spouse, person_data):
        assert spouse.firstname == person_data['spouse']['spouseName']
        assert spouse.lastname == person_data['surname']
        assert spouse.prevlastname == person_data['spouse']['originalFamily']
        assert spouse.sex == 'f'
        assert spouse.profession.name == person_data['spouse']['profession']
        assert spouse.marriageyear == population_utils.int_or_none(person_data['spouse']['weddingYear'])

        assert spouse.birthplace.name == person_data['spouse']['birthData']['birthLocation']
        assert spouse.birthdate.day == population_utils.int_or_none(person_data['spouse']['birthData']['birthDay'])
        assert spouse.birthdate.month == population_utils.int_or_none(person_data['spouse']['birthData']['birthMonth'])
        assert spouse.birthdate.year == population_utils.int_or_none(person_data['spouse']['birthData']['birthYear'])

        assert spouse.deathdate is None

    # TODO: Place populating with Levenshtein