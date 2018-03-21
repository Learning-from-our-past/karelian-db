import re

lastname_regex_options = (re.UNICODE | re.IGNORECASE)
lastname_regex_patterns = (r'(?P<lastname>[\w-]+)[,.]?\sent(?:[,.]\s)?',
                          r'^ent([,.]\s)?(?P<lastname>[\w-]+)$')

LASTNAME_REGEXES = tuple(re.compile(x, lastname_regex_options) for x in lastname_regex_patterns)


def clean_up_name_string(name_string):
    return name_string.replace(' ', '').replace('-', '')


def find_former_lastnames(former_lastname):
    """
    Finds a person's former lastnames from a formerSurname string in a MiKARELIA
    database row.
    :param former_lastname: a formerSurname string from a MiKARELIA database row
    :return: a tuple containing all of the person's former surnames
    """
    former_lastnames = []
    if former_lastname:
        former_lastname = former_lastname.casefold()
        former_lastname = former_lastname.replace('(', '')
        former_lastname = former_lastname.replace(')', '')
        if ' ' in former_lastname:
            for regex in LASTNAME_REGEXES:
                lastname_match = regex.search(former_lastname)
                if lastname_match:
                    lastname = lastname_match.group('lastname')
                    former_lastnames.append(clean_up_name_string(lastname))
        else:
            former_lastname = former_lastname.replace('-', '')
            former_lastnames.append(former_lastname)
    return tuple(former_lastnames)
