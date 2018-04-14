import pytest
from datalinking.event_id_combiner import EventIdCombiner
from collections import namedtuple


class TestEventIdCombiner:
    mock_person = namedtuple('MockPerson', 'db_id event_ids')

    @pytest.fixture(autouse=True, scope='function')
    def combiner(self):
        return EventIdCombiner()

    @staticmethod
    def check_combiner_data(combiner, num_families=None, num_db_ids=None, num_event_ids=None):
        if num_families is not None:
            assert len(combiner.families) == num_families
        if num_db_ids is not None:
            assert len(combiner.db_id2family_id) == num_db_ids
        if num_event_ids is not None:
            assert len(combiner.event_id2family_id) == num_event_ids

    @staticmethod
    def check_family_data(family, event_ids=None, db_ids=None):
        if event_ids is not None:
            assert set(family['event_ids']) == event_ids
        if db_ids is not None:
            assert set(family['db_ids']) == db_ids

    def should_combine_event_ids_together_when_they_have_been_previously_encountered(self, combiner):
        mock_data = {0: self.mock_person(db_id=0, event_ids={1, 2, 3}),
                     1: self.mock_person(db_id=1, event_ids={3, 4, 5}),
                     2: self.mock_person(db_id=2, event_ids={2, 6, 7})}

        combiner.create_family_id_maps(mock_data)
        family = next(iter(combiner.families.values()))
        expected_event_ids = {e_id for person in mock_data.values() for e_id in person.event_ids}

        self.check_combiner_data(combiner, num_families=1, num_db_ids=len(mock_data),
                                 num_event_ids=len(expected_event_ids))
        self.check_family_data(family, event_ids=expected_event_ids, db_ids=mock_data.keys())

    def should_combine_event_ids_together_when_there_are_two_previously_separate_families_that_are_bridged_by_person_with_event_ids_in_both_families(self, combiner):
        mock_data = {0: self.mock_person(db_id=0, event_ids={1, 2, 3}),
                     1: self.mock_person(db_id=1, event_ids={11, 12, 13}),
                     2: self.mock_person(db_id=2, event_ids={3, 8, 13})}
        # the person with key 2 links people 0 and 1 together because person 2 has
        # event_ids 3 and 13

        combiner.create_family_id_maps(mock_data)
        family = next(iter(combiner.families.values()))
        expected_event_ids = {e_id for person in mock_data.values() for e_id in person.event_ids}

        self.check_combiner_data(combiner, num_families=1, num_db_ids=len(mock_data),
                                 num_event_ids=len(expected_event_ids))
        self.check_family_data(family, event_ids=expected_event_ids, db_ids=mock_data.keys())

    def should_not_combine_event_ids_together_when_there_is_no_event_id_links_between_people(self, combiner):
        mock_data = {0: self.mock_person(db_id=0, event_ids={1, 2, 3}),
                     1: self.mock_person(db_id=1, event_ids={11, 12, 13}),
                     2: self.mock_person(db_id=2, event_ids={21, 22, 23})}

        combiner.create_family_id_maps(mock_data)
        self.check_combiner_data(combiner, num_families=len(mock_data),
                                 num_db_ids=len(mock_data),
                                 num_event_ids=9)
        for family in combiner.families.values():
            assert len(family['db_ids']) == 1
            db_id = family['db_ids'][0]
            self.check_family_data(family, event_ids=mock_data[db_id].event_ids)
