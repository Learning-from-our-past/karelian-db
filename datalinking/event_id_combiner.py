from tqdm import tqdm


class EventIdCombiner:
    def __init__(self):
        self.event_id2family_id = {}
        self.db_id2family_id = {}
        self.families = {}

    def create_family_id_maps(self, data):
        """
        Creates family ID maps out of person data with an event_ids attribute.
        :param data: A dict of db_id: person_data
        :return: Three dicts: 1) event_id2family_id, 2) db_id2family_id, 3) families
        """
        for db_id, person in tqdm(data.items()):
            # We need to be able to access event_ids by index
            event_ids = tuple(person.event_ids)
            found_family_ids = self._find_existing_families(event_ids)

            if len(found_family_ids) == 0:
                self._create_new_family(event_ids, (db_id,))
            elif len(found_family_ids) == 1:
                found_family_id = found_family_ids.pop()
                self._update_family(found_family_id, event_ids, (db_id,))
            else:
                self._combine_families(found_family_ids, event_ids, (db_id,))

    def _find_existing_families(self, event_ids):
        """
        Determine if any of the previously encountered families contain one of these event IDs.
        :param event_ids: Event IDs to try and find families for
        :return: IDs of all families that contained any of the event IDs
        """
        found_families_ids = set()
        for event_id in event_ids:
            if event_id in self.event_id2family_id:
                found_families_ids.add(self.event_id2family_id[event_id])
        return found_families_ids

    def _create_new_family(self, e_ids, db_ids):
        key = '{}{}'.format(str(db_ids[0]), e_ids[0])
        sid = {'event_ids': e_ids, 'db_ids': db_ids}
        self.families.update({key: sid})
        self._update_id_maps(key, e_ids, db_ids)

    def _combine_families(self, family_ids, e_ids, db_ids):
        """
        Combines two or more families, with the new family having all of the event_ids
        and db_ids from the old families AND the person who linked the families together.
        :param family_ids: IDs of families to combine
        :param e_ids: Event IDs of the person who linked the families together
        :param db_ids: The person's DB id
        """
        old_families = [self.families.pop(f_id) for f_id in family_ids]
        e_ids_combined = tuple({e_id for entry in old_families for e_id in entry['event_ids']} | set(e_ids))
        db_ids_combined = tuple({db_id for entry in old_families for db_id in entry['db_ids']} | set(db_ids))
        self._create_new_family(e_ids_combined, db_ids_combined)

    def _update_family(self, family_id, e_ids, db_ids):
        """
        Updates an existing family to add new event IDs and DB IDs to it.
        :param family_id: ID of family to update
        :param e_ids: Event IDs to add to family
        :param db_ids: DB IDs to add to family
        """
        family = self.families[family_id]
        known_eids = family['event_ids']
        combined_eids = set(known_eids).union(e_ids)
        family['event_ids'] = tuple(combined_eids)
        family['db_ids'] += db_ids
        self._update_id_maps(family_id, e_ids, db_ids)

    def _update_id_maps(self, family_id, e_ids, db_ids):
        for e_id in e_ids:
            self.event_id2family_id[e_id] = family_id
        for db_id in db_ids:
            self.db_id2family_id[db_id] = family_id
