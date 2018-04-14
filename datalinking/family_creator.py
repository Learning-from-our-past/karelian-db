class FamilyCreator:
    def __init__(self, katiha_families, db_id2family_id, katiha_data):
        self._ka_families = katiha_families
        self._d2f = db_id2family_id
        self._ka_data = katiha_data
        self.families = None
        self.kaira_id2family_id = None

    def create_families(self, link_data):
        """
        Creates families using link data.
        :param link_data: List of linked people in tuples: (katiha_id, kaira_id)
        """
        self.families = {}
        self.kaira_id2family_id = {}
        self._make_families_out_of_linked_people(link_data)
        self._add_katihalians_to_families(link_data)

        # There is something wrong with the Katiha data and they have some gigantic families,
        # through data exploration it has been determined that families larger than 30 children
        # are safe to remove and should be removed.
        for family_id, family in list(self.families.items()):
            if len(family) > 30:
                for ka_person, mk_person in family:
                    if mk_person is not None:
                        del self.kaira_id2family_id[mk_person]
                del self.families[family_id]

    def _make_families_out_of_linked_people(self, link_data):
        """
        Make MiKARELIAn families utilizing the link data and the katiha family data.
        :param link_data:
        :return: Dict of familyId keys and list of tuples that are family members. Tuples are
        formatted as (katiha_person_cleaned namedtuple, kaira_id)
        """
        for mk_person, ka_person in link_data:
            f_id = self._d2f.get(ka_person, None)
            if f_id:
                if f_id not in self.families:
                    self.families[f_id] = [[self._ka_data[ka_person], mk_person]]
                else:
                    self.families[f_id].append([self._ka_data[ka_person], mk_person])
                self.kaira_id2family_id[mk_person] = f_id

    def _add_katihalians_to_families(self, link_data):
        """
        Add Katihalians who have no MiKARELIAn link but one of their siblings does have a
        MiKARELIAn link back into the families.
        """
        katihalians_with_link = {katihalian for mikarelian, katihalian in link_data}
        for f_id, f in self.families.items():
            additional_katihalians = [(self._ka_data[db_id], None)
                                      for db_id in self._ka_families[f_id]['db_ids']
                                      if db_id not in katihalians_with_link]
            f += additional_katihalians
