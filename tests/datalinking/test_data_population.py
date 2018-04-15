import pytest
from db_management.update_report import update_report
from db_management.exceptions import NoFamilyIdAndKairaIdException
from tests.datalinking.data.mock_link_data import MOCK_DATA
from tests.datalinking.data.mock_link_data import get_mock_katiha_person_creator
from datalinking.data_populater import populate_linked_data
from datalinking.utils.db_utils import get_katiha_families_and_number_linked_family_members
from db_management.siirtokarjalaistentie_models import Person
from db_management.katiha_models import *
from peewee import fn


class TestDataPopulation:
    @pytest.fixture(autouse=True, scope='function', name='link_data')
    def populate_link_data_to_db(self, person_data, database):
        update_report.setup('mock_link_data')
        populate_linked_data(database, MOCK_DATA)
        return MOCK_DATA

    @pytest.fixture(autouse=True, scope='function', name='katiha_person')
    def read_katiha_person(self):
        return KatihaPerson.get()

    def should_populate_katiha_person_correctly(self, link_data, katiha_person):
        assert katiha_person.id == link_data[0].db_id
        assert katiha_person.birthDay == link_data[0].date_of_birth[0]
        assert katiha_person.birthMonth == link_data[0].date_of_birth[1]
        assert katiha_person.birthYear == link_data[0].date_of_birth[2]
        assert katiha_person.sex == link_data[0].sex
        assert katiha_person.multipleBirth == link_data[0].multiple_birth
        assert katiha_person.vaccinated == link_data[0].vaccinated
        assert katiha_person.rokko == link_data[0].rokko
        assert katiha_person.literate == link_data[0].literate
        assert katiha_person.literacyConfirmed == link_data[0].literacy_confirmed
        mikarelia_person = Person.get(Person.katihaId == katiha_person.id)
        assert mikarelia_person.kairaId == link_data[0].link_kaira_id

    def should_populate_family_correctly(self, link_data, katiha_person):
        # Not much to test here yet
        family = Family.get(Family.id == katiha_person.familyId)
        assert family.id == link_data[0].family_id

    def should_populate_language_correctly(self, link_data, katiha_person):
        language = Language.get(Language.id == katiha_person.motherLanguageId)
        assert language.language == link_data[0].mother_language

    def should_populate_birth_in_marriage_correctly(self, link_data, katiha_person):
        birth_in_marriage = BirthInMarriageCode.get(BirthInMarriageCode.code == katiha_person.birthInMarriage)
        assert birth_in_marriage.birthType == link_data[0].birth_in_marriage

    def should_set_up_links_correctly(self, link_data):
        links = Person.select(Person.katihaId).tuples()
        links = {link[0] for link in links}
        assert link_data[0].db_id in links
        assert None in links  # FIXME: if the mock data is changed to include more non-links,
        # it may be wise to count the number of None in links instead of / before making it a set.
        assert link_data[3].db_id in links
        assert link_data[1].db_id not in links
        assert link_data[2].db_id not in links
        assert link_data[4].db_id not in links

    def should_add_non_linked_family_members_for_linked_family_members(self, link_data):
        family_id_and_num_members = (
            KatihaPerson.select(KatihaPerson.familyId,
                                fn.COUNT(KatihaPerson.familyId).alias('num_members'))
                        .group_by(KatihaPerson.familyId)
        )
        family_id_and_num_linked_members = get_katiha_families_and_number_linked_family_members()
        expected_members = [(1, 3), (2, 2)]
        expected_linked_members = [(1, 1), (2, 1)]
        result_members = [(result.familyId.id, result.num_members)
                          for result in family_id_and_num_members]
        result_linked_members = [(result.katihaId.familyId.id, result.num_linked_members)
                                 for result in family_id_and_num_linked_members]

        assert expected_members == result_members and expected_linked_members == result_linked_members

    def should_correctly_clean_up_people_who_are_not_in_pickle_from_database(self, database, link_data):
        populate_linked_data(database, MOCK_DATA[0:2])
        mikarelia_person = Person.get(Person.kairaId == link_data[3].link_kaira_id)

        assert mikarelia_person.katihaId is None
        assert KatihaPerson.select().count() == 2
        assert Family.select().count() == 1
        assert Language.select().count() == 1

    def should_not_let_populate_a_person_without_family_id_and_kaira_id(self, database):
        mock_person = get_mock_katiha_person_creator()
        mocked_katiha_person = mock_person(link_kaira_id=None, family_id=None)
        with pytest.raises(NoFamilyIdAndKairaIdException):
            populate_linked_data(database, [mocked_katiha_person])
