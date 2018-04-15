from enum import Enum


def get_code_map(enumeration):
    return {code.value: code.name.replace('_', ' ') for code in enumeration}


class BirthInMarriageCodes(Enum):
    """
    These codes were obtained through email correspondence with the Katiha people.
    For some reason they are not included in the Katiha rekisteriseloste or in the
    Katiha database's codes table.
    """
    born_in_wedlock = 1
    born_out_of_wedlock = 2
    born_to_engaged_parents = 3
