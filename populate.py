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
        'name': spouse['SpouseBirthData']['BirthLocation'],
        'latitude': 0,
        'longitude': 0,
        'region': '',
        'location': None
    })[0]

    profession = _populate_profession({
        'name': spouse['SpouseProfession']
    })[0]

    birth_date = _populate_person_date({
        'day': spouse['SpouseBirthData']['BirthDay'],
        'month':  spouse['SpouseBirthData']['BirthMonth'],
        'year':  spouse['SpouseBirthData']['BirthYear']
    })

    if spouse['spouseDeathYear']:
        death_date = _populate_person_date({
            'day': None,
            'month':  None,
            'year': spouse['spouseDeathYear']
        })
    else:
        death_date = None

    spouseData = {
        'firstname': spouse['SpouseName'],
        'lastname': person['Surname'],
        'prevlastname': spouse['SpouseOriginalFamily'],
        'sex': _invert_gender(person['Gender']),
        'birthdate': birth_date,
        'birthplace': birth_place,
        'deathdate': death_date,
        'profession': profession,
        'spouse': personModel,
        'marriageyear': spouse['WeddingYear'] or None
    }

    return Spouse.create_or_get(**spouseData)

def _populate_child(child, personModel, person):
    birth_date = _populate_person_date({
        'day': None,
        'month': None,
        'year': child['birthYear']
    })

    location = None
    if child['childCoordinates']['latitude'] and child['childCoordinates']['longitude']:
        location = pft(child['childCoordinates']['latitude'], child['childCoordinates']['longitude'])

    birth_place = _populate_place({
        'name': child['locationName'],
        'latitude': child['childCoordinates']['latitude'] or 0,
        'longitude': child['childCoordinates']['longitude'] or 0,
        'location': location,
        'region': ''
    })[0]

    childData = {
        'firstname': child['name'],
        'lastname': person['Surname'],
        'sex':  _transform_sex(child['gender']),
        'birthdate': birth_date,
        'birthplace': birth_place,
        'parent': personModel
    }

    return Child.create_or_get(**childData)

def _populate_migration_record(record):
    return Livingrecord.create_or_get(**record)

def _populate_migration_history(region, places, personModel):
    for p in places:

        if region == 'karelia':
            location = None
            if p['KarelianCoordinates']['longitude'] and p['KarelianCoordinates']['latitude']:
                location = pft(p['KarelianCoordinates']['longitude'], p['KarelianCoordinates']['latitude'])

            placeModel = _populate_place({
                'name': p['KarelianLocation'],
                'latitude': p['KarelianCoordinates']['latitude'] or 0,
                'longitude': p['KarelianCoordinates']['longitude'] or 0,
                'region': region or '',
                'location': location
            })[0]
        elif region == 'finland':
            location = None
            if p['OtherCoordinates']['longitude'] and p['OtherCoordinates']['latitude']:
                location = pft(p['OtherCoordinates']['longitude'], p['OtherCoordinates']['latitude'])

            placeModel = _populate_place({
                'name': p['OtherLocation'],
                'latitude': p['OtherCoordinates']['latitude'] or 0,
                'longitude': p['OtherCoordinates']['longitude'] or 0,
                'region': region or '',
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
        'name': person['BirthLocation'],
        'latitude': 0,
        'longitude': 0,
        'region': '',
        'location': None
    })[0]

    page = _populate_page({
        'pagenumber': person['ApproximatePageNumber']
    })[0]

    profession = _populate_profession({
        'name': person['Profession/Status']
    })[0]

    birth_date = _populate_person_date({
        'day': person['BirthDay'],
        'month': person['BirthMonth'],
        'year': person['BirthYear']
    })

    death_date = None
    death_place = None

    personData = {
        'firstname': person['FirstNames'],
        'lastname': person['Surname'],
        'prevlastname': person['OriginalFamily'],
        'sex': _transform_sex(person['Gender']),
        'birthdate': birth_date,
        'birthplace': birth_place,
        'deathdate': death_date,
        'deathplace': death_place,
        'ownhouse': person['Omakotitalo'],
        'profession': profession,
        'returnedkarelia': person['ReturnedToKarelia'],
        'previousmarriages': person['MaybePreviousMarriages'],
        'pagenumber': page,
        'origtext': person['originalText']
    }

    personModel = Person.create_or_get(**personData)[0]

    if person['Spouse']['HasSpouse']:
        spouseModel = _populate_spouse(person['Spouse'], personModel, person)[0]

    for child in person['Children']:
        childModel = _populate_child(child, personModel, person)[0]

    _populate_migration_history('karelia', person['KarelianLocations'], personModel)
    _populate_migration_history('finland', person['OtherLocations'], personModel)



