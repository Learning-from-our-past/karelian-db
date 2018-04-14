class DatalinkingDictMaker:
    def __init__(self, grouping_keys, identifying_key=None):
        """
        :param grouping_keys: List of strings which are keys used to group data in the
        datalinking dict.
        :param identifying_key: Key used for representing each data point in the deepest
        level of the dict structure. If not provided, the data point itself is used.
        """
        if len(grouping_keys) < 1:
            raise NoGroupingKeysException()
        self._keys = grouping_keys
        self._id_key = identifying_key
        self._link_dict = {}

    def make_datalinking_dict(self, data):
        """
        Makes a datalinking dict where person data is grouped by attributes for quick lookup
        and data linking.
        :param data: A dict of db_id: person_data, where person_data is a namedtuple and should
        at least have the attributes specified in the grouping keys given to the constructor,
        and the identifying key
        :return: A dict with the people grouped by date of birth and normalized last name
        """
        # TODO: If we want to support dicts as well as namedtuples, add logic to determine whether
        # the user specified a dict or a namedtuple and pick a 'get' function based on that.
        for person in data.values():
            key_reached, sub_dict = self._find_existing_keys_in_link_dict(person)

            if self._id_key is not None:
                identifying_value = getattr(person, self._id_key)
            else:
                identifying_value = person

            if key_reached == self._keys[-1]:
                sub_dict.append(identifying_value)
            else:
                key_values = [getattr(person, key) for key in self._keys]
                if key_reached is None:
                    immediate_key = key_values[0]
                    build_path = key_values[1:]
                else:
                    index_reached = self._keys.index(key_reached)
                    immediate_key = key_values[index_reached+1]
                    build_path = key_values[index_reached+2:]
                sub_dict[immediate_key] = self._create_nested_dict(build_path, [identifying_value])

        return self._link_dict

    def _find_existing_keys_in_link_dict(self, person):
        key_reached = None
        sub_dict = self._link_dict
        for key in self._keys:
            value = getattr(person, key)
            if value in sub_dict:
                sub_dict = sub_dict[value]
                key_reached = key
            else:
                break
        return key_reached, sub_dict

    def _create_nested_dict(self, nesting_keys, nested_value):
        """
        Creates a nested dict with as many levels as there are nesting keys provided.
        :param nesting_keys: Keys used for creation of nested dicts
        :param nested_value: Value placed at the deepest level of the nested dicts
        :return:
        """
        if len(nesting_keys) > 1:
            return {nesting_keys.pop(0): self._create_nested_dict(nesting_keys, nested_value)}
        elif len(nesting_keys) == 1:
            return {nesting_keys.pop(0): nested_value}
        else:
            return nested_value


class NoGroupingKeysException(Exception):
    def __init__(self):
        super().__init__('At least one grouping key must be specified!')
