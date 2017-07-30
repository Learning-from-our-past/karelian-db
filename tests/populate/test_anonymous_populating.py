import pytest

import config
import tests.utils.population_utils as population_utils
from db_management.models.db_siirtokarjalaistentie_models import *
from tests.utils.dbUtils import DBUtils


@pytest.yield_fixture(autouse=True, scope='module', name='anon_data')
def populate_person_information_to_db():
    config.CONFIG['anonymize'] = True
    DBUtils.truncate_db()
    # Person data is anonymized and tweaked and only usable for software testing.
    return population_utils.populate_from_json("./tests/populate/data/person1.json")[0]


class TestPersonPopulate:

    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def should_have_populated_anonymous_person_correctly(self, person, anon_data):
        assert person.firstName is None
        assert person.lastName is None
        assert person.prevLastName is None
        assert person.ownHouse == anon_data['ownHouse']['results']
        assert person.sex == 'm'
        assert person.returnedKarelia == 'true'
        assert person.previousMarriages == 'false'
        assert person.originalText is None

        assert person.birthDay == anon_data['birthday']['results']['birthDay']
        assert person.birthMonth == anon_data['birthday']['results']['birthMonth']
        assert person.birthYear == anon_data['birthday']['results']['birthYear']
        assert person.deathDay is None
        assert person.deathMonth is None
        assert person.deathYear is None

    def should_have_populated_anonymous_children_correctly(self, person, anon_data):
        child = (Child.select()
                 .join(Place, on=(Place.id == Child.birthPlaceId))
                 .where(Child.fatherId == person.id))[0]

        # Only one child
        expected_child = anon_data['children']['results']['children'][0]
        assert child.firstName is None
        assert child.lastName is None
        assert child.sex == 'm'
        assert child.birthYear == population_utils.int_or_none(expected_child['birthYear'])

        assert child.birthPlaceId.name == expected_child['location']['locationName']
        assert child.birthPlaceId.latitude == expected_child['location']['coordinates']['latitude']
        assert child.birthPlaceId.longitude == expected_child['location']['coordinates']['longitude']

    def should_have_populated_anonymous_spouse_correctly(self, person, anon_data):
        marriage = Marriage.select().where(Marriage.manId == person.id).get()

        assert marriage.weddingYear == anon_data['spouse']['results']['weddingYear']['results']

        spouse = (Person.select()
                  .join(Place, on=(Place.id == Person.birthPlaceId))
                  .join(Profession, on=(Profession.id == Person.professionId))
                  .where(Person.id == marriage.womanId))[0]

        assert spouse.firstName is None
        assert spouse.lastName is None
        assert spouse.prevLastName is None
        assert spouse.originalText is None
        assert spouse.sex == 'f'
        assert spouse.professionId.name == anon_data['spouse']['results']['profession']['results']

        assert spouse.birthPlaceId.name == anon_data['spouse']['results']['birthData']['birthLocation']['results']['locationName']
        assert spouse.birthDay == population_utils.int_or_none(anon_data['spouse']['results']['birthData']['results']['birthDay'])
        assert spouse.birthMonth == population_utils.int_or_none(anon_data['spouse']['results']['birthData']['results']['birthMonth'])
        assert spouse.birthYear == population_utils.int_or_none(anon_data['spouse']['results']['birthData']['results']['birthYear'])

        assert spouse.deathDay is None
        assert spouse.deathMonth is None
        assert spouse.deathYear is None
