from abc import ABC
from abc import abstractmethod
from datalinking.support_data.place_names import ALTERNATIVE_MIKARELIA_NAMES_FOR_KATIHA_PLACE
from datalinking.utils.datalinking_dict import DatalinkingDictMaker
from datalinking.utils.linking_utils import is_birthplace_same
from datalinking.utils.linking_utils import is_firstname_same
from datalinking.utils.linking_utils import are_firstnames_same


class DataLinker(ABC):
    def __init__(self, from_data, to_data):
        """
        This class attempts to link person information from one set of data to another. Set
        the data in this constructor and then call find_links.
        :param from_data: The data whose people are tried to link to other data
        :param to_data: The data we are trying to link people to
        """
        self._from = from_data
        self._to = to_data
        dict_maker = DatalinkingDictMaker(['date_of_birth', 'normalized_last_name'], 'db_id')
        self._datalinking_dict = dict_maker.make_datalinking_dict(to_data)

    @abstractmethod
    def find_links(self):
        pass


class MiKARELIA2KatihaLinker(DataLinker):
    def find_links(self):
        """
        Tries to link person data across data sets.
        :return: A list of tuples with identifiers of match pairs.
        """
        matches = []
        match_fn = self._match_by_normalized_first_name_and_birthplace_or_normalized_names
        for person in self._from.values():
            # With this syntax we avoid writing a lot of 'in' checks
            last_name_matches = self._datalinking_dict.get(person.date_of_birth, {})\
                                                      .get(person.normalized_last_name, None)
            if last_name_matches:
                matched_person = match_fn(person, last_name_matches)
                if matched_person:
                    matches.append((person.db_id, matched_person))
        return matches

    def _match_by_normalized_first_name_and_birthplace_or_normalized_names(self, person, possible_matches):
        """
        Find matches for person in pool of possible matches, using normalized first name and
        birthplace or all normalized names as matching criteria.
        :param person: Data of one person (needle) to match to another
        :param possible_matches: Pool of people (haystack) to try and find the match in
        :return:
        """
        for possible_match in possible_matches:
            m_data = self._to[possible_match]
            if self._is_match_based_on_norm_first_name_and_birthplace(person, m_data):
                return possible_match
            elif are_firstnames_same(person, m_data):
                return possible_match
        return None

    def _is_match_based_on_norm_first_name_and_birthplace(self, person, possible_match):
        # See place_names.py for why we do this alternative place names thing
        alternative_place_names = ALTERNATIVE_MIKARELIA_NAMES_FOR_KATIHA_PLACE.get(
            possible_match.birthplace, set()
        )
        is_match = is_firstname_same(person, possible_match)
        is_match &= (is_birthplace_same(person, possible_match) or
                     person.birthplace in alternative_place_names)
        return is_match
