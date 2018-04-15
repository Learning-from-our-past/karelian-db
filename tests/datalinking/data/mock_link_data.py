from datalinking.data_formatter import KatihaPerson


def get_mock_katiha_person_creator():
    current_id = 0

    def get_mock_katiha_person(db_id=None, event_ids={'e1'}, normalized_first_names=('nyymi',),
                               normalized_last_name='testikäs', date_of_birth=(1, 1, 1900),
                               birthplace='testilä', mother_language='finnish', link_kaira_id=None,
                               family_id=None, sex=None, birth_in_marriage=None, multiple_birth=None,
                               vaccinated=None, rokko=None, literate=None, literacy_confirmed=None,
                               departure_type=None, departure_date=None):
        if db_id is None:
            nonlocal current_id
            current_id += 1
            db_id = current_id
        return KatihaPerson(db_id=db_id, event_ids=event_ids,
                            normalized_first_names=normalized_first_names,
                            normalized_last_name=normalized_last_name,
                            date_of_birth=date_of_birth, birthplace=birthplace,
                            mother_language=mother_language, link_kaira_id=link_kaira_id,
                            family_id=family_id, sex=sex, birth_in_marriage=birth_in_marriage,
                            multiple_birth=multiple_birth, vaccinated=vaccinated, rokko=rokko,
                            literate=literate, literacy_confirmed=literacy_confirmed,
                            departure_type=departure_type, departure_date=departure_date)
    return get_mock_katiha_person


mock_person = get_mock_katiha_person_creator()


MOCK_DATA = [
    mock_person(date_of_birth=(1, 5, 1900), mother_language='finnish',
                link_kaira_id='siirtokarjalaiset_1_1P', family_id=1, sex='f',
                birth_in_marriage='born out of wedlock', multiple_birth=3,
                vaccinated=True, rokko=False, literate=True, literacy_confirmed=True,
                departure_type='died', departure_date=(2, 5, 1900)),
    mock_person(date_of_birth=(3, 4, 1901), mother_language='finnish',
                link_kaira_id=None, family_id=1),
    mock_person(date_of_birth=(7, 1, 1904), mother_language='finnish',
                link_kaira_id=None, family_id=1),
    mock_person(date_of_birth=(1, 5, 1900), mother_language='swedish',
                link_kaira_id='siirtokarjalaiset_1_2P', family_id=2),
    mock_person(date_of_birth=(1, 5, 1900), mother_language='swedish',
                link_kaira_id=None, family_id=2)
]
