import pytest
from tests.utils.dbUtils import DBUtils
import tests.utils.population_utils as population_utils
from models.db_siirtokarjalaistentie_models import *
import config

@pytest.yield_fixture(autouse=True, scope='module', name='person_data')
def populate_person_information_to_db():
    config.CONFIG['anonymize'] = False
    DBUtils.truncate_db()
    # Person data is anonymized and tweaked and only usable for software testing.
    return population_utils.populate_from_json("./tests/populate/data/person1.json")[0]


class TestPersonPopulate:
    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def test_person_data_was_populated_correctly(self, person, person_data):
        assert person.firstName == person_data['name']['results']['firstNames']
        assert person.lastName == person_data['name']['results']['surname']
        assert person.prevLastName == person_data['originalFamily']['results']
        assert person.ownHouse == person_data['ownHouse']['results']
        assert person.sex == 'm'
        assert person.returnedKarelia == 'true'
        assert person.previousMarriages == 'false'
        assert person.originalText == person_data['personMetadata']['results']['originalText']

        assert person.birthDay == person_data['birthday']['results']['birthDay']
        assert person.birthMonth == person_data['birthday']['results']['birthMonth']
        assert person.birthYear == person_data['birthday']['results']['birthYear']
        assert person.deathDay is None
        assert person.deathMonth is None
        assert person.deathYear is None

    def test_profession_was_populated_correctly(self, person, person_data):
        profession = Profession.get(Profession.id == person.professionId)
        assert profession.name == person_data['profession']['results']

    def test_page_was_populated_correctly(self, person, person_data):
        page = Page.get(Page.pageNumber == person.pageNumber)
        assert page.pageNumber == person_data['personMetadata']['results']['approximatePageNumber']

    def test_living_records_were_populated_correctly(self, person, person_data):
        records = sorted(Livingrecord.select().join(Place).where(Livingrecord.personId == person.id), key = lambda x: (x.movedIn is None, x.movedIn))

        expected_records = sorted(person_data['migrationHistory']['results']['locations'], key=lambda x: (x['movedIn'] is None, x['movedIn']))
        assert len(records) == len(expected_records)

        for i, r in enumerate(records):
            assert r.movedIn == population_utils.int_or_none(expected_records[i]['movedIn'])
            assert r.movedOut == population_utils.int_or_none(expected_records[i]['movedOut'])

            assert r.placeId.name == expected_records[i]['locationName']

            assert r.placeId.latitude == expected_records[i]['coordinates']['latitude']
            assert r.placeId.longitude == expected_records[i]['coordinates']['longitude']

            assert r.placeId.region == expected_records[i]['region']

    def test_children_were_populated_correctly(self, person, person_data):
        child = (Child.select()
                 .join(Place, on=(Place.id == Child.birthPlaceId))
                 .where(Child.fatherId == person.id))[0]

        # Only one child
        expected_child = person_data['children']['results']['children'][0]
        assert child.firstName == expected_child['name']
        assert child.sex == 'm'
        assert child.birthYear == population_utils.int_or_none(expected_child['birthYear'])

        assert child.birthPlaceId.name == expected_child['location']['locationName']
        assert child.birthPlaceId.latitude == expected_child['location']['coordinates']['latitude']
        assert child.birthPlaceId.longitude == expected_child['location']['coordinates']['longitude']

    def test_spouse_data_was_populated_correctly(self, person, person_data):
        marriage = Marriage.select().where(Marriage.manId == person.id).get()

        assert marriage.weddingYear == person_data['spouse']['results']['weddingYear']['results']

        spouse = (Person.select()
                  .join(Place, on=(Place.id == Person.birthPlaceId))
                  .join(Profession, on=(Profession.id == Person.professionId))
                  .where(Person.id == marriage.womanId))[0]

        assert spouse.firstName == person_data['spouse']['results']['spouseName']
        assert spouse.lastName == person_data['name']['results']['surname']
        assert spouse.prevLastName == person_data['spouse']['results']['originalFamily']['results']
        assert spouse.sex == 'f'
        assert spouse.professionId.name == person_data['spouse']['results']['profession']['results']

        assert spouse.birthPlaceId.name == person_data['spouse']['results']['birthData']['birthLocation']['results']['locationName']
        assert spouse.birthDay == population_utils.int_or_none(person_data['spouse']['results']['birthData']['results']['birthDay'])
        assert spouse.birthMonth == population_utils.int_or_none(person_data['spouse']['results']['birthData']['results']['birthMonth'])
        assert spouse.birthYear == population_utils.int_or_none(person_data['spouse']['results']['birthData']['results']['birthYear'])

        assert spouse.deathDay is None
        assert spouse.deathMonth is None
        assert spouse.deathYear is None


# TODO:
# should fill in coordinates if they are not set but not modify coordinates if they are set already in existing Place