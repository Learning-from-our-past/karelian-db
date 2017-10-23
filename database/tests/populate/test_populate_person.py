import pytest

import common.testing.population_utils as population_utils
from common.siirtokarjalaistentie_models import *


class TestPersonPopulate:
    @pytest.yield_fixture(autouse=True, scope='class')
    def person(self):
        return Person.get()

    def should_have_populated_person_correctly(self, person, person_data):
        assert person.firstName == person_data[0]['primaryPerson']['name']['firstNames']
        assert person.lastName == person_data[0]['primaryPerson']['name']['surname']
        assert person.formerSurname == person_data[0]['primaryPerson']['formerSurname']
        assert person.ownHouse == person_data[0]['primaryPerson']['ownHouse']
        assert person.sex == 'm'
        assert person.returnedKarelia == 'true'
        assert person.previousMarriages == 'false'
        assert person.originalText == person_data[0]['personMetadata']['sourceText']

        assert person.birthDay == person_data[0]['primaryPerson']['birthData']['birthDay']
        assert person.birthMonth == person_data[0]['primaryPerson']['birthData']['birthMonth']
        assert person.birthYear == person_data[0]['primaryPerson']['birthData']['birthYear']
        assert person.deathDay is None
        assert person.deathMonth is None
        assert person.deathYear is None
        assert person.lotta == person_data[0]['primaryPerson']['warData']['lottaActivityFlag']
        assert person.servedDuringWar == person_data[0]['primaryPerson']['warData']['servedDuringWarFlag']
        assert person.injuredInWar == person_data[0]['primaryPerson']['warData']['injuredInWarFlag']

    def should_have_populated_profession_correctly(self, person, person_data):
        profession = Profession.get(Profession.id == person.professionId)
        assert profession.name == person_data[0]['primaryPerson']['profession']['professionName']

    def should_have_populated_page_correctly(self, person, person_data):
        page = Page.get(Page.pageNumber == person.pageNumber)
        assert page.pageNumber == person_data[0]['personMetadata']['approximatePageNumber']

    def should_have_populated_living_records_correctly(self, person, person_data):
        records = sorted(LivingRecord.select().join(Place).where(LivingRecord.personId == person.id), key = lambda x: (x.movedIn is None, x.movedIn))

        expected_records = sorted(person_data[0]['primaryPerson']['migrationHistory']['locations'], key=lambda x: (x['movedIn'] is None, x['movedIn']))
        assert len(records) == len(expected_records)

        for i, r in enumerate(records):
            assert r.movedIn == population_utils.int_or_none(expected_records[i]['movedIn'])
            assert r.movedOut == population_utils.int_or_none(expected_records[i]['movedOut'])

            assert r.placeId.name == expected_records[i]['locationName']

            assert r.placeId.latitude == expected_records[i]['coordinates']['latitude']
            assert r.placeId.longitude == expected_records[i]['coordinates']['longitude']

            assert r.placeId.region == expected_records[i]['region']

    def should_have_populated_children_correctly(self, person, person_data):
        child_models = (Child.select()
                 .join(Place, on=(Place.id == Child.birthPlaceId))
                 .where(Child.fatherId == person.id)).order_by(Child.kairaId)

        def _transform_sex(sex):
            if sex == 'Female':
                return 'f'
            else:
                return 'm'

        # Two children
        for expected_child, child in zip(person_data[0]['children'], child_models):
            assert child.firstName == expected_child['name']
            assert child.sex == _transform_sex(expected_child['gender'])
            assert child.birthYear == population_utils.int_or_none(expected_child['birthYear'])

            assert child.birthPlaceId.name == expected_child['location']['locationName']
            assert child.birthPlaceId.latitude == expected_child['location']['coordinates']['latitude']
            assert child.birthPlaceId.longitude == expected_child['location']['coordinates']['longitude']

    def should_have_populated_spouse_correctly(self, person, person_data):
        marriage = Marriage.select().where(Marriage.manId == person.id).get()

        assert marriage.weddingYear == person_data[0]['spouse']['weddingYear']

        spouse = (Person.select()
                  .join(Place, on=(Place.id == Person.birthPlaceId))
                  .join(Profession, on=(Profession.id == Person.professionId))
                  .where(Person.id == marriage.womanId))[0]

        assert spouse.firstName == person_data[0]['spouse']['firstNames']
        assert spouse.lastName == person_data[0]['primaryPerson']['name']['surname']
        assert spouse.formerSurname == person_data[0]['spouse']['formerSurname']
        assert spouse.sex == 'f'
        assert spouse.professionId.name == person_data[0]['spouse']['profession']['professionName']

        assert spouse.birthPlaceId.name == person_data[0]['spouse']['birthData']['birthLocation']['locationName']
        assert spouse.birthDay == population_utils.int_or_none(person_data[0]['spouse']['birthData']['birthDay'])
        assert spouse.birthMonth == population_utils.int_or_none(person_data[0]['spouse']['birthData']['birthMonth'])
        assert spouse.birthYear == population_utils.int_or_none(person_data[0]['spouse']['birthData']['birthYear'])

        assert spouse.deathDay is None
        assert spouse.deathMonth is None
        assert spouse.deathYear is None

        assert spouse.lotta == person_data[0]['spouse']['warData']['lottaActivityFlag']
        assert spouse.servedDuringWar == person_data[0]['spouse']['warData']['servedDuringWarFlag']
        assert spouse.injuredInWar == person_data[0]['spouse']['warData']['injuredInWarFlag']


class TestFarmDetailsPopulate:

    def should_have_populated_farm_details_correctly(self):
        farm_details = list(FarmDetails.select())

        # There should be only one farm details which contains some true flags
        assert len(farm_details) == 1
        assert farm_details[0].maanhankintalaki is True
        assert farm_details[0].animalHusbandry is True
        assert farm_details[0].dairyFarm is False
        assert farm_details[0].farmTotalArea == 53.2

        # Two of the persons should have id to farm details while one does not have any
        persons = list(Person.select())
        assert persons[0].kairaId == 'siirtokarjalaiset_1_1P' and persons[0].farmDetailsId.id is not None
        assert persons[1].kairaId == 'siirtokarjalaiset_1_1S_1' and persons[1].farmDetailsId.id is not None
        assert persons[0].farmDetailsId.id == persons[1].farmDetailsId.id

        assert persons[2].kairaId == 'siirtokarjalaiset_1_2P' and persons[2].farmDetailsId is None


class TestProfessionPopulate:

    def should_have_populated_all_professions_correctly(self):
        professions = list(Profession.select().order_by(Profession.name))

        assert professions[0].name == 'emäntä'
        assert professions[0].SESgroup1989 == 1
        assert professions[0].socialClassRank == 5
        assert professions[0].occupationCategory == 3
        assert professions[0].agricultureOrForestryRelated is True
        assert professions[0].education is False

        assert professions[1].name == 'kirvesmies'
        assert professions[1].SESgroup1989 is None
        assert professions[1].socialClassRank is None
        assert professions[1].occupationCategory is None
        assert professions[1].agricultureOrForestryRelated is None
        assert professions[1].education is None

        assert professions[2].name == 'maanviljelijä'

# TODO:
# should fill in coordinates if they are not set but not modify coordinates if they are set already in existing Place
