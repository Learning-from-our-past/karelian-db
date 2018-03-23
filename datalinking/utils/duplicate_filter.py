def get_duplicate_filter(attributes, identifying_attribute=None):
    """
    Returns a function that can identify whether a given namedtuple has been been
    encountered before.
    :param attributes: Iterable of strings which are attributes used for detecting
    duplicates. If column contains a comma, the integer found after the comma is
    used as an index to access the Nth element of attribute instead of using the
    entire attribute variable.
    :param identifying_attribute: Attribute used to uniquely identify rows. If omitted,
    entire object is used.
    :return: Function
    """
    already_encountered = {}
    key_fmt = '{}' * len(attributes)

    def find_duplicate_key(row):
        """
        Attempts to determine whether the provided row is a duplicate or not based on
        attributes provided to the higher order function.
        :param row: namedtuple that must at least have the attributes specified in
        columns to higher order function and, if specified, identifying_attribute
        :return: If duplicate is not found: False. If duplicate is found:
        identifying_attribute of previously encountered row if identifying_attribute
        was provided to higher order function, otherwise previously encountered row.
        """
        key_values = []
        for attribute in attributes:
            if ',' in attribute:
                comma_index = attribute.index(',')
                actual_attribute = attribute[:comma_index]
                index = int(attribute[comma_index+1:])
                key_values.append(getattr(row, actual_attribute)[index])
            else:
                key_values.append(getattr(row, attribute))
        key = key_fmt.format(*key_values)

        if key in already_encountered:
            return already_encountered[key]

        already_encountered[key] = getattr(row, identifying_attribute)
        return False

    return find_duplicate_key
