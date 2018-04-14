from collections import Counter


def get_frequency_collater(data_key):
    """
    Returns a function that can be used to collate data with specified key. The
    collater does simple logic and returns collated value. None if value can not
    easily be collated, otherwise the most frequency value.
    :param data_key: string, key of value to collate
    :return:
    """
    id2values = {}

    def collate(primary_id, person):
        """
        :param primary_id: db_id of the unique person we are collating the data under
        :param person: the duplicate we are processing
        :return: dict that can be used to update collated_dict
        """
        new_value = getattr(person, data_key)
        id2values.setdefault(primary_id, Counter()).update([new_value])
        values = id2values[primary_id]
        collated_value = new_value
        if len(values) > 1:
            collated_value = None
            if None in values and len(values) == 2:
                collated_value = next(l for l in values.keys() if l)
        return {data_key: collated_value}
    return collate
