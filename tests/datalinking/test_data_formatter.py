import pytest
from datalinking.data_formatter import DataFormatter
from datalinking.data_cleaner import katiha_person_cleaned
from itertools import zip_longest
from collections import OrderedDict


def get_mock_katiha_person_creator():
    current_id = 0

    def get_mock_katiha_person(db_id=None, event_ids={'e1'}, normalized_first_names=('nyymi',),
                               normalized_last_name='testikäs', date_of_birth=(1, 1, 1900),
                               birthplace='testilä', mother_language='finnish', sex=None,
                               birth_in_marriage=None, multiple_birth=None):
        if db_id is None:
            nonlocal current_id
            current_id += 1
            db_id = current_id
        return katiha_person_cleaned(db_id=db_id, event_ids=event_ids,
                                     normalized_first_names=normalized_first_names,
                                     normalized_last_name=normalized_last_name,
                                     date_of_birth=date_of_birth, birthplace=birthplace,
                                     mother_language=mother_language, sex=sex,
                                     birth_in_marriage=birth_in_marriage,
                                     multiple_birth=multiple_birth)
    return get_mock_katiha_person


def make_mock_family(katihalians, num_mikarelians):
    """
    Makes a mock family in the same format as FamilyCreator does using the katiha people provided
    and the first num_mikarelians number of katiha people have a kaira_id link, the rest don't.
    :param katihalians: Katiha people to use for mock family creation
    :param num_mikarelians: Number of Katiha people that should have a MiKARELIAn link
    :return:
    """
    mock_family = []
    kaira_ids = ['kaira{}'.format(katihalians[x].db_id) for x in range(num_mikarelians)]
    for katihalian, kaira_id in zip_longest(katihalians, kaira_ids, fillvalue=None):
        mock_family.append((katihalian, kaira_id))
    return mock_family


class TestDataFormatter:
    @pytest.fixture(autouse=True, scope='function')
    def mocker(self):
        return get_mock_katiha_person_creator()

    def should_format_data_into_a_list_correctly(self, mocker):
        # FIXME: We need to create a lot of mock data to test this component, find a better way
        # to do this?
        mock_katiha_data = OrderedDict((x, mocker()) for x in range(1, 11))
        list_mock_katiha_data = list(mock_katiha_data.values())
        mock_link_data = [('kaira{}'.format(x.db_id), x.db_id) for x in list_mock_katiha_data[:7]]
        del mock_link_data[3]
        mock_families = {'family1': make_mock_family(list_mock_katiha_data[:4], 3),
                         'family2': make_mock_family(list_mock_katiha_data[4:6], 2),
                         'family3': make_mock_family(list_mock_katiha_data[6:8], 1)}
        mock_families['family1'].append((list_mock_katiha_data[8], None))
        mock_link_data.append(('kaira{}'.format(list_mock_katiha_data[9].db_id), list_mock_katiha_data[9].db_id))
        mock_kaira_id2_family_id = {mk: family_id for family_id, family in mock_families.items()
                                    for ka, mk in family if mk is not None}

        data_formatter = DataFormatter(mock_kaira_id2_family_id, mock_families, mock_katiha_data)
        katiha_people = data_formatter.get_katiha_people_with_kaira_and_family_ids(mock_link_data)
        data = [(person.link_kaira_id, person.family_id) for person in katiha_people]
        expected_data = [('kaira1', 1), ('kaira2', 1), ('kaira3', 1), (None, 1), (None, 1),
                         ('kaira5', 2), ('kaira6', 2),
                         ('kaira7', 3), (None, 3),
                         ('kaira10', None)]
        assert data == expected_data
