from datalinking.support_data.place_names import KATIHA_PARISH_ID_TO_BIRTHPLACE_NAME
from datalinking.support_data.place_names import KATIHA_BIRTHPARISH_TO_MIKARELIA_BIRTHPLACE


def resolve_birthplace_to_mikarelia_birthplace(person):
    """
    Attempts to resolve the given person's birth parish or ID to a MiKARELIA compatible
    birthplace.
    :param person: A namedtuple('KatihaPersonRaw')
    :return: A string with the person's birthplace
    """
    if person.birthParish:
        birth_parish = person.birthParish.strip().casefold().replace('-', '')
    else:
        birth_parish = None

    if not birth_parish or birth_parish == 'täällä':
        birthplaces = KATIHA_PARISH_ID_TO_BIRTHPLACE_NAME[int(person.parishId)]
        birthplace = birthplaces['mikarelia_name'].casefold()
    elif birth_parish in KATIHA_BIRTHPARISH_TO_MIKARELIA_BIRTHPLACE:
        birthplace = KATIHA_BIRTHPARISH_TO_MIKARELIA_BIRTHPLACE[birth_parish]
    else:
        birthplace = birth_parish

    return birthplace
