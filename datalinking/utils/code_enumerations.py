from enum import Enum

"""
The Katiha rekisteriseloste referenced in this file is located at:
http://www.karjalatk.fi/rekisteriseloste2015.rtf
Accessed 2018-04-16T19:33:22+00:00
"""


def get_code_map(enumeration):
    return {code.value: code.name.replace('_', ' ') for code in enumeration}


def get_code_set(enumeration):
    return {code.value for code in enumeration}


class BirthInMarriageCodes(Enum):
    """
    These codes were obtained through email correspondence with the Katiha people.
    For some reason they are not included in the Katiha rekisteriseloste or in the
    Katiha database's codes table.
    """
    born_in_wedlock = 1
    born_out_of_wedlock = 2
    born_to_engaged_parents = 3


class WasVaccinatedCodes(Enum):
    """
    These codes were obtained from both the Katiha rekisteriseloste and from emails
    with the Katiha people.
    """
    had_rokko_disease_and_was_vaccinated = '3'
    was_vaccinated_alternative_one = '1'
    was_vaccinated_alternative_two = 'v'
    was_vaccinated_alternative_three = 'r'


class WasNotVaccinatedCodes(Enum):
    """
    These codes were obtained from the Katiha rekisteriseloste.
    """
    was_not_vaccinated = '2'


class RokkoDiseaseCodes(Enum):
    """
    These codes were obtained from both the Katiha rekisteriseloste and from emails
    with the Katiha people.
    """
    had_rokko_disease_and_was_vaccinated = '3'
    had_rokko_disease_alternative_one = '2'
    had_rokko_disease_alternative_two = 's'


class DepartureTypeCodes(Enum):
    """
    These codes were obtained from the Katiha rekisteriseloste.
    """
    emigrated = 0
    died = 2
    to_other_parish = 5
    to_other_religion = 6


class MotherLanguageCodes(Enum):
    """
    These codes were obtained from the Katiha rekisteriseloste.
    """
    other = 0
    finnish = 1
    swedish = 2
    russian = 3
    german = 4
