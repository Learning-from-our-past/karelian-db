from models.db_siirtokarjalaistentie_models import *

def _transform_sex(orig):
    if orig == 'Male':
        return 'm'
    elif orig == 'Female':
        return 'f'
    else:
        return ''

def _invert_gender(orig):
    if orig == 'Male':
        return 'f'
    elif orig == 'Female':
        return 'm'
    else:
        return ''

def _populate_place(place):
    return Place.get_or_create(**place)

def _populate_page(page):
    return Page.get_or_create(**page)

def _populate_profession(profession):
    return Profession.get_or_create(**profession)

def _populate_person_date(date):
    if not date['day'] and not date['month'] and not date['year']:
        return None

    # If there is date violating date checks, ignore it
    try:
        return Persondate.get_or_create(**date)[0]
    except IntegrityError:
        return None

def _populate_spouse(spouse, personModel, person):
    birth_place = _populate_place({
        'name': spouse['birthData']['birthLocation'],
        'latitude': 0,
        'longitude': 0,
        'region': '',
        'location': None
    })[0]

    profession = _populate_profession({
        'name': spouse['profession']
    })[0]

    birth_date = _populate_person_date({
        'day': spouse['birthData']['birthDay'],
        'month':  spouse['birthData']['birthMonth'],
        'year':  spouse['birthData']['birthYear']
    })

    if spouse['deathYear']:
        death_date = _populate_person_date({
            'day': None,
            'month':  None,
            'year': spouse['deathYear']
        })
    else:
        death_date = None

    spouseData = {
        'firstname': spouse['spouseName'],
        'lastname': person['surname'],
        'prevlastname': spouse['originalFamily'],
        'sex': _invert_gender(person['gender']),
        'birthdate': birth_date,
        'birthplace': birth_place,
        'deathdate': death_date,
        'profession': profession,
        'spouse': personModel,
        'marriageyear': spouse['weddingYear'] or None
    }

    return Spouse.create_or_get(**spouseData)

def _populate_child(child, personModel, person):
    birth_date = _populate_person_date({
        'day': None,
        'month': None,
        'year': child['birthYear']
    })

    location = None
    if child['coordinates']['latitude'] and child['coordinates']['longitude']:
        location = pft(child['coordinates']['latitude'], child['coordinates']['longitude'])

    birth_place = _populate_place({
        'name': child['location'],
        'latitude': child['coordinates']['latitude'] or 0,
        'longitude': child['coordinates']['longitude'] or 0,
        'location': location,
        'region': ''
    })[0]

    childData = {
        'firstname': child['name'],
        'lastname': person['surname'],
        'sex':  _transform_sex(child['gender']),
        'birthdate': birth_date,
        'birthplace': birth_place,
        'parent': personModel
    }

    return Child.create_or_get(**childData)

def _populate_migration_record(record):
    return Livingrecord.create_or_get(**record)

def _populate_migration_history(places, personModel):
    for p in places:
        location = None
        if p['coordinates']['longitude'] and p['coordinates']['latitude']:
            location = pft(p['coordinates']['longitude'], p['coordinates']['latitude'])

        placeModel = _populate_place({
            'name': p['locationName'],
            'latitude': p['coordinates']['latitude'] or 0,
            'longitude': p['coordinates']['longitude'] or 0,
            'region': p['region'] or '',
            'location': location
        })[0]

        if not p['movedIn']:
            p['movedIn'] = None

        if not p['movedOut']:
            p['movedOut'] = None

        _populate_migration_record({
            'person': personModel,
            'place': placeModel,
            'movedin':  p['movedIn'],
            'movedout': p['movedOut']
        })[0]

def populate_person(person):
    birth_place = _populate_place({
        'name': person['birthLocation'],
        'latitude': 0,
        'longitude': 0,
        'region': '',
        'location': None
    })[0]

    page = _populate_page({
        'pagenumber': person['approximatePageNumber']
    })[0]

    profession = _populate_profession({
        'name': person['profession']
    })[0]

    birth_date = _populate_person_date({
        'day': person['birthDay'],
        'month': person['birthMonth'],
        'year': person['birthYear']
    })

    death_date = None
    death_place = None

    personData = {
        'firstname': person['firstNames'],
        'lastname': person['surname'],
        'prevlastname': person['originalFamily'],
        'sex': _transform_sex(person['gender']),
        'birthdate': birth_date,
        'birthplace': birth_place,
        'deathdate': death_date,
        'deathplace': death_place,
        'ownhouse': person['omakotitalo'],
        'profession': profession,
        'returnedkarelia': person['returnedToKarelia'],
        'previousmarriages': person['maybePreviousMarriages'],
        'pagenumber': page,
        'origtext': person['originalText']
    }

    personModel = Person.create_or_get(**personData)[0]

    if person['spouse']['hasSpouse']:
        spouseModel = _populate_spouse(person['spouse'], personModel, person)[0]

    for child in person['children']:
        childModel = _populate_child(child, personModel, person)[0]

    _populate_migration_history(person['locations'], personModel)



