import pytest
import tests.utils.population_utils as population_utils
from db_management.models.db_siirtokarjalaistentie_models import *


class TestPersonPopulate:
    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def should_have_populated_person_correctly(self, person, person_data):
        assert person.firstName == person_data[0]['name']['results']['firstNames']
        assert person.lastName == person_data[0]['name']['results']['surname']
        assert person.prevLastName == person_data[0]['originalFamily']['results']
        assert person.ownHouse == person_data[0]['ownHouse']['results']
        assert person.sex == 'm'
        assert person.returnedKarelia == 'true'
        assert person.previousMarriages == 'false'
        assert person.originalText == person_data[0]['personMetadata']['results']['originalText']

        assert person.birthDay == person_data[0]['birthday']['results']['birthDay']
        assert person.birthMonth == person_data[0]['birthday']['results']['birthMonth']
        assert person.birthYear == person_data[0]['birthday']['results']['birthYear']
        assert person.deathDay is None
        assert person.deathMonth is None
        assert person.deathYear is None

    def should_have_populated_profession_correctly(self, person, person_data):
        profession = Profession.get(Profession.id == person.professionId)
        assert profession.name == person_data[0]['profession']['results']

    def should_have_populated_page_correctly(self, person, person_data):
        page = Page.get(Page.pageNumber == person.pageNumber)
        assert page.pageNumber == person_data[0]['personMetadata']['results']['approximatePageNumber']

    def should_have_populated_living_records_correctly(self, person, person_data):
        records = sorted(Livingrecord.select().join(Place).where(Livingrecord.personId == person.id), key = lambda x: (x.movedIn is None, x.movedIn))

        expected_records = sorted(person_data[0]['migrationHistory']['results']['locations'], key=lambda x: (x['movedIn'] is None, x['movedIn']))
        assert len(records) == len(expected_records)

        for i, r in enumerate(records):
            assert r.movedIn == population_utils.int_or_none(expected_records[i]['movedIn'])
            assert r.movedOut == population_utils.int_or_none(expected_records[i]['movedOut'])

            assert r.placeId.name == expected_records[i]['locationName']

            assert r.placeId.latitude == expected_records[i]['coordinates']['latitude']
            assert r.placeId.longitude == expected_records[i]['coordinates']['longitude']

            assert r.placeId.region == expected_records[i]['region']

    def should_have_populated_children_correctly(self, person, person_data):
        child = (Child.select()
                 .join(Place, on=(Place.id == Child.birthPlaceId))
                 .where(Child.fatherId == person.id))[0]

        # Only one child
        expected_child = person_data[0]['children']['results']['children'][0]
        assert child.firstName == expected_child['name']
        assert child.sex == 'm'
        assert child.birthYear == population_utils.int_or_none(expected_child['birthYear'])

        assert child.birthPlaceId.name == expected_child['location']['locationName']
        assert child.birthPlaceId.latitude == expected_child['location']['coordinates']['latitude']
        assert child.birthPlaceId.longitude == expected_child['location']['coordinates']['longitude']

    def should_have_populated_spouse_correctly(self, person, person_data):
        marriage = Marriage.select().where(Marriage.manId == person.id).get()

        assert marriage.weddingYear == person_data[0]['spouse']['results']['weddingYear']['results']

        spouse = (Person.select()
                  .join(Place, on=(Place.id == Person.birthPlaceId))
                  .join(Profession, on=(Profession.id == Person.professionId))
                  .where(Person.id == marriage.womanId))[0]

        assert spouse.firstName == person_data[0]['spouse']['results']['spouseName']
        assert spouse.lastName == person_data[0]['name']['results']['surname']
        assert spouse.prevLastName == person_data[0]['spouse']['results']['originalFamily']['results']
        assert spouse.sex == 'f'
        assert spouse.professionId.name == person_data[0]['spouse']['results']['profession']['results']

        assert spouse.birthPlaceId.name == person_data[0]['spouse']['results']['birthData']['birthLocation']['results']['locationName']
        assert spouse.birthDay == population_utils.int_or_none(person_data[0]['spouse']['results']['birthData']['results']['birthDay'])
        assert spouse.birthMonth == population_utils.int_or_none(person_data[0]['spouse']['results']['birthData']['results']['birthMonth'])
        assert spouse.birthYear == population_utils.int_or_none(person_data[0]['spouse']['results']['birthData']['results']['birthYear'])

        assert spouse.deathDay is None
        assert spouse.deathMonth is None
        assert spouse.deathYear is None


# TODO:
# should fill in coordinates if they are not set but not modify coordinates if they are set already in existing Place