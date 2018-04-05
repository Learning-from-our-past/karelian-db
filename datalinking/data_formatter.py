from datalinking.data_cleaner import katiha_person_cleaned
from collections import namedtuple

KatihaPerson = namedtuple('KatihaPerson',
                          katiha_person_cleaned._fields + ('link_kaira_id', 'family_id'))


class DataFormatter:
    def __init__(self, kaira_id2family_id, families, katiha_data):
        """
        :param kaira_id2family_id: A dict mapping kairaIds (as keys) to familyIds (as values)
        :param families: A dict with familyId as key and a list of family members as value. The
        family members are tuples of (katiha_person_cleaned, kaira_id).
        :param katiha_data: A dict with katiha people with katiha db id as key and a
        katiha_person_cleaned namedtuple as the value.
        """
        self._k2f = kaira_id2family_id
        self._families = families
        self._ka_data = katiha_data
        self._katiha_people = None
        self._added_families = None

    def get_katiha_people_with_kaira_and_family_ids(self, link_data):
        """
        Takes link data and returns a list of Katiha people with kairaIds and familyIds added
        to them. The list also contains Katiha people who don't have a link in MiKARELIA but
        have a family member who has a link in MiKARELIA data.
        :param link_data: A list of tuples of format (kaira_id, katiha_id)
        :return: A list of katiha_person_nt namedtuples
        """
        self._added_families = set()
        self._katiha_people = []

        for mk_person, ka_person in link_data:
            family_id = self._k2f.get(mk_person, None)
            if family_id is not None and family_id not in self._added_families:
                self._add_family_members(family_id)
            elif family_id is None:
                self._add_person(self._ka_data[ka_person],
                                 kaira_id=mk_person,
                                 assign_family_id=False)

        return self._katiha_people

    def _add_person(self, katiha_person_data, kaira_id, assign_family_id):
        family_id = None
        if assign_family_id:
            family_id = len(self._added_families)

        katiha_person = KatihaPerson(*katiha_person_data,
                                     link_kaira_id=kaira_id,
                                     family_id=family_id)
        self._katiha_people.append(katiha_person)

    def _add_family_members(self, family_id):
        family = self._families[family_id]
        self._added_families.add(family_id)
        for katihalian, mikarelian in family:
            kaira_id = None
            if mikarelian is not None:
                kaira_id = mikarelian
            self._add_person(katihalian,
                             kaira_id=kaira_id,
                             assign_family_id=True)
