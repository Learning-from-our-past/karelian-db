import pytest

import common.database_config as config
import common.testing.population_utils as population_utils
import db_management.preprocess_operations as preproc
from common.siirtokarjalaistentie_models import *
from common.testing.dbUtils import DBUtils
from db_management.update_database import update_data_in_db


class TestPersonPopulate:

    @pytest.yield_fixture(autouse=True, scope='class', name='person_data')
    def populate_person_information_to_db_anonymized(self, database): # Override the root populating fixture
        config.CONFIG['anonymize'] = True
        DBUtils.truncate_db()
        # Person data is anonymized and tweaked and only usable for software testing.
        return population_utils.populate_from_json(database, "./tests/populate/data/person.json")[0]

    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def should_have_populated_anonymous_person_correctly(self, person, person_data):
        assert person.firstName is None
        assert person.lastName is None
        assert person.formerSurname is None
        assert person.ownHouse == person_data['primaryPerson']['ownHouse']
        assert person.sex == 'm'
        assert person.returnedKarelia == 'true'
        assert person.previousMarriages == 'false'
        assert person.originalText is None

        assert person.birthDay == person_data['primaryPerson']['birthData']['birthDay']
        assert person.birthMonth == person_data['primaryPerson']['birthData']['birthMonth']
        assert person.birthYear == person_data['primaryPerson']['birthData']['birthYear']
        assert person.deathDay is None
        assert person.deathMonth is None
        assert person.deathYear is None

    def should_have_populated_anonymous_children_correctly(self, person, person_data):
        child_models = (Child.select()
                 .join(Place, on=(Place.id == Child.birthPlaceId))
                 .where(Child.fatherId == person.id)).order_by(Child.kairaId)

        def _transform_sex(sex):
            if sex == 'Female':
                return 'f'
            else:
                return 'm'

        # Two children
        for expected_child, child in zip(person_data['children'], child_models):
            assert child.firstName is None
            assert child.lastName is None
            assert child.sex == _transform_sex(expected_child['gender'])
            assert child.birthYear == population_utils.int_or_none(expected_child['birthYear'])

            assert child.birthPlaceId.name == expected_child['location']['locationName']
            assert child.birthPlaceId.latitude == expected_child['location']['coordinates']['latitude']
            assert child.birthPlaceId.longitude == expected_child['location']['coordinates']['longitude']

    def should_not_delete_anonymous_children_if_there_is_no_changes(self, person, person_data, mocker):
        person_models = []

        delete_spy = mocker.patch.object(preproc, '_delete_children_of_person',
                                         wraps=preproc._delete_children_of_person)

        for data_entry in [person_data]:
            person_models.append(update_data_in_db(data_entry, population_utils.MockRecord()))

        assert delete_spy.call_count == 0

    def should_have_populated_anonymous_spouse_correctly(self, person, person_data):
        marriage = Marriage.select().where(Marriage.manId == person.id).get()

        assert marriage.weddingYear == person_data['spouse']['weddingYear']

        spouse = (Person.select()
                  .join(Place, on=(Place.id == Person.birthPlaceId))
                  .join(Profession, on=(Profession.id == Person.professionId))
                  .where(Person.id == marriage.womanId))[0]

        assert spouse.firstName is None
        assert spouse.lastName is None
        assert spouse.formerSurname is None
        assert spouse.originalText is None
        assert spouse.sex == 'f'
        assert spouse.professionId.name == person_data['spouse']['profession']['professionName']

        assert spouse.birthPlaceId.name == person_data['spouse']['birthLocation']['locationName']
        assert spouse.birthDay == population_utils.int_or_none(person_data['spouse']['birthData']['birthDay'])
        assert spouse.birthMonth == population_utils.int_or_none(person_data['spouse']['birthData']['birthMonth'])
        assert spouse.birthYear == population_utils.int_or_none(person_data['spouse']['birthData']['birthYear'])

        assert spouse.deathDay is None
        assert spouse.deathMonth is None
        assert spouse.deathYear is None
