import pytest
from datalinking.data_cleaner import katiha_person_cleaned
from datalinking.data_cleaner import mikarelia_person_cleaned
from datalinking.utils.datalinking_dict import DatalinkingDictMaker
from datalinking.utils.datalinking_dict import NoGroupingKeysException
from datalinking.data_linker import MiKARELIA2KatihaLinker
from collections import OrderedDict
from collections import namedtuple


def mock_mikarelia_person(db_id='kaira1', date_of_birth=(1, 1, 1900), normalized_last_name='testinen',
                          normalized_first_names=('testikäs',), birthplace='nyymilä'):
    return mikarelia_person_cleaned(db_id=db_id, date_of_birth=date_of_birth,
                                    normalized_last_name=normalized_last_name,
                                    normalized_first_names=normalized_first_names,
                                    birthplace=birthplace)


def mock_katiha_person(db_id=1, date_of_birth=(1, 1, 1900), normalized_last_name='testinen',
                       normalized_first_names=('testikäs',), birthplace='testilä',
                       mother_language='testikieli', event_ids={'mock_id'}):
    return katiha_person_cleaned(db_id=db_id, date_of_birth=date_of_birth,
                                 normalized_last_name=normalized_last_name,
                                 normalized_first_names=normalized_first_names,
                                 birthplace=birthplace, mother_language=mother_language,
                                 event_ids=event_ids)


def check_link_data(from_data, to_data, expected_length=None):
    linker = MiKARELIA2KatihaLinker(OrderedDict((f.db_id, f) for f in from_data),
                                    OrderedDict((t.db_id, t) for t in to_data))
    link_data = linker.find_links()
    if expected_length is not None:
        assert len(link_data) == expected_length
    else:
        expected_link_data = [(f.db_id, t.db_id) for f, t in zip(from_data, to_data)]
        assert link_data == expected_link_data


class TestDataLinker:
    class TestMiKARELIA2KatihaLinker:
        def should_correctly_link_two_people_who_share_firstname_and_birthplace(self):
            first_names = ('nyymikäs', 'testikäs')
            last_name = 'nyyminen'
            birthplace = 'nyymilä'

            mk_person = mock_mikarelia_person(normalized_first_names=first_names,
                                              normalized_last_name=last_name,
                                              birthplace=birthplace)
            ka_person = mock_katiha_person(normalized_first_names=first_names,
                                           normalized_last_name=last_name,
                                           birthplace=birthplace)

            check_link_data([mk_person], [ka_person])

        def should_correctly_link_two_people_with_different_birthplace_but_same_firstnames(self):
            first_names = ('nyymikäs', 'testikäs', 'salaisa')
            last_name = 'nyyminen'

            mk_person = mock_mikarelia_person(normalized_first_names=first_names,
                                              normalized_last_name=last_name,
                                              birthplace='nyymilä')
            # first name order shouldn't matter, so reverse it
            ka_person = mock_katiha_person(normalized_first_names=first_names[::-1],
                                           normalized_last_name=last_name,
                                           birthplace='nyymila')

            check_link_data([mk_person], [ka_person])

        def should_not_link_two_people_with_same_firstnames_but_different_birthplace_if_there_are_not_enough_firstnames(self):
            first_names = ('nyymikäs',)
            last_name = 'nyyminen'

            mk_person = mock_mikarelia_person(normalized_first_names=first_names,
                                              normalized_last_name=last_name,
                                              birthplace='nyymilä')
            ka_person = mock_katiha_person(normalized_first_names=first_names,
                                           normalized_last_name=last_name,
                                           birthplace='nyymila')

            check_link_data([mk_person], [ka_person], expected_length=0)

        def should_not_link_two_people_who_have_nothing_in_common(self):
            mk_person = mock_mikarelia_person()
            ka_person = mock_katiha_person(normalized_first_names=(mk_person.normalized_first_names[0][::-1],),
                                           normalized_last_name=mk_person.normalized_last_name[::-1],
                                           date_of_birth=mk_person.date_of_birth[::-1],
                                           birthplace=mk_person.birthplace[::-1])

            check_link_data([mk_person], [ka_person], expected_length=0)


class TestDatalinkDictCreation:
    def should_correctly_make_datalinking_dict_with_arbitrary_grouping_keys_and_arbitrary_identifier(self):
        grouping_keys = ['key1', 'cat', 'key3']
        arbitrary_nt = namedtuple('Arbitrary', grouping_keys + ['dog_id'])
        test_data = arbitrary_nt(key1='123', cat='abc', key3='456', dog_id='shiba42')
        expected_data = {test_data.key1: {test_data.cat: {test_data.key3: [test_data.dog_id]}}}
        m = DatalinkingDictMaker(grouping_keys, 'dog_id')
        datalinking_dict = m.make_datalinking_dict({test_data.dog_id: test_data})
        assert expected_data == datalinking_dict

    def should_correctly_make_datalinking_dict_with_only_one_grouping_key(self):
        ka_person = mock_katiha_person()
        m = DatalinkingDictMaker(['date_of_birth'])
        datalinking_dict = m.make_datalinking_dict({ka_person.db_id: ka_person})
        assert datalinking_dict == {ka_person.date_of_birth: [ka_person]}

    def should_correctly_make_datalinking_dict_with_multiple_date_of_births(self):
        ka_person = mock_katiha_person()
        ka_person_reversed = mock_katiha_person(db_id=2, date_of_birth=ka_person.date_of_birth[::-1],
                                                normalized_last_name=ka_person.normalized_last_name[::-1],
                                                normalized_first_names=(ka_person.normalized_first_names[0][::-1],),)

        expected_data = {ka_person.date_of_birth: {ka_person.normalized_last_name: [ka_person.db_id]},
                         ka_person_reversed.date_of_birth: {ka_person_reversed.normalized_last_name: [ka_person_reversed.db_id]}}
        m = DatalinkingDictMaker(['date_of_birth', 'normalized_last_name'], 'db_id')
        datalinking_dict = m.make_datalinking_dict({ka_person.db_id: ka_person,
                                                    ka_person_reversed.db_id: ka_person_reversed})
        assert datalinking_dict == expected_data

    def should_correctly_group_multiple_people_with_same_date_of_birth_together(self):
        test_data = [mock_katiha_person(),
                     mock_katiha_person(db_id=2, normalized_last_name='nyymilä',
                                        normalized_first_names=('hullu', 'poro')),
                     mock_katiha_person(db_id=3, normalized_last_name='salainen',
                                        normalized_first_names=('nopea', 'koira'))]

        m = DatalinkingDictMaker(['date_of_birth', 'normalized_last_name'], 'db_id')
        datalinking_dict = m.make_datalinking_dict({person.db_id: person for person in test_data})
        assert set(datalinking_dict[(1, 1, 1900)].keys()) == {person.normalized_last_name for person in test_data}

    def should_correctly_group_multiple_people_with_same_date_of_birth_and_last_name_together(self):
        test_data = [mock_katiha_person(),
                     mock_katiha_person(db_id=2, normalized_first_names=('hidas', 'elefantti')),
                     mock_katiha_person(db_id=3, normalized_first_names=('ovela', 'kettu'))]

        m = DatalinkingDictMaker(['date_of_birth', 'normalized_last_name'], 'db_id')
        datalinking_dict = m.make_datalinking_dict({person.db_id: person for person in test_data})
        assert datalinking_dict[(1, 1, 1900)]['testinen'] == [person.db_id for person in test_data]

    def should_raise_exception_if_there_are_zero_grouping_keys(self):
        with pytest.raises(NoGroupingKeysException):
            DatalinkingDictMaker([])
