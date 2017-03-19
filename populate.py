from models.db_siirtokarjalaistentie_models import *
from config import CONFIG

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
    """
    When populating new Place to the database, try to figure out if place already exists there either as directly or
    one with slightly different name. Use Postgres Levenshtein search to find group of similar named places and
    then try to use one of the existing if there is either coordinate match or region match. Otherwise create a new
    record.
    :param place:
    :return:
    """

    if place['name'] is None or place['name'] == '':
        return None

    if CONFIG['place_levenshtein']:
        existing_places = Place.raw("select * "
                                    "from siirtokarjalaisten_tie.place "
                                    "where levenshtein(place.name, %s, 1, 2, 3) <= 3 "
                                    "order by levenshtein(place.name, %s)", place['name'], place['name'])

        coordinates_available = place['latitude'] and place['longitude']

        if coordinates_available:
            places_with_same_coordinates = [p for p in existing_places if p.latitude == place['latitude'] and p.longitude == place['longitude']]

            if len(places_with_same_coordinates) > 0:
                # Place with same coordinates should be same place -> use it
                existing_place = places_with_same_coordinates[0]
                # Fill in missing region if there is not one in db
                if existing_place.region == '' and place['region'] != '':
                    existing_place.region = place['region']

                existing_place.save()
                return existing_place

        # Check if there is place with same region
        places_with_same_region = [p for p in existing_places
                                   if p.region != ''
                                   and p.region == place['region']]

        if len(places_with_same_region) > 0:
            existing_place = places_with_same_region[0]

            # Fill in the coordinates to existing record if they are missing
            if existing_place.latitude == '' and existing_place.longitude == '' and coordinates_available:
                existing_place.latitude = place['latitude']
                existing_place.longitude = place['longitude']
                existing_place.save()
            return existing_place

    return Place.get_or_create(**place)[0]

def _populate_page(page):
    return Page.get_or_create(**page)

def _populate_profession(profession):
    if profession['name'] is None:
        return None, None
    else:
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
        'name': spouse['birthData']['birthLocation']['results'],
        'latitude': None,
        'longitude': None,
        'region': None,
        'location': None
    })
    profession = _populate_profession({
        'name': spouse['profession']['results']
    })[0]

    birth_date = _populate_person_date({
        'day': spouse['birthData']['results']['birthDay'],
        'month':  spouse['birthData']['results']['birthMonth'],
        'year':  spouse['birthData']['results']['birthYear']
    })

    if spouse['deathYear'] is not None:
        death_date = _populate_person_date({
            'day': None,
            'month':  None,
            'year': spouse['deathYear']['results']
        })
    else:
        death_date = None

    spouseData = {
        'firstname': spouse['spouseName'],
        'lastname': person['name']['results']['surname'],
        'prevlastname': spouse['originalFamily']['results'],
        'sex': _invert_gender(person['name']['results']['gender']),
        'birthdate': birth_date,
        'birthplace': birth_place,
        'deathdate': death_date,
        'profession': profession,
        'spouse': personModel,
        'marriageyear': spouse['weddingYear']['results'] or None
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
    })

    childData = {
        'firstname': child['name'],
        'lastname': person['name']['results']['surname'],
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
            'latitude': p['coordinates']['latitude'],
            'longitude': p['coordinates']['longitude'],
            'region': p['region'],
            'location': location
        })

        _populate_migration_record({
            'person': personModel,
            'place': placeModel,
            'movedin':  p['movedIn'],
            'movedout': p['movedOut']
        })[0]

def populate_person(person):
    birth_place = _populate_place({
        'name': person['birthLocation']['results'],
        'latitude': None,
        'longitude': None,
        'region': None,
        'location': None
    })

    page = _populate_page({
        'pagenumber': person['personMetadata']['results']['approximatePageNumber']
    })[0]

    profession = _populate_profession({
        'name': person['profession']['results']
    })[0]

    birth_date = _populate_person_date({
        'day': person['birthday']['results']['birthDay'],
        'month': person['birthday']['results']['birthMonth'],
        'year': person['birthday']['results']['birthYear'],
    })

    death_date = None
    death_place = None

    personData = {
        'firstname': person['name']['results']['firstNames'],
        'lastname': person['name']['results']['surname'],
        'prevlastname': person['originalFamily']['results'],
        'sex': _transform_sex(person['name']['results']['gender']),
        'birthdate': birth_date,
        'birthplace': birth_place,
        'deathdate': death_date,
        'deathplace': death_place,
        'ownhouse': person['ownHouse']['results'],
        'profession': profession,
        'returnedkarelia': person['migrationHistory']['results']['returnedToKarelia'],
        'previousmarriages': None,  # FIXME: This is missing from new data set.
        'pagenumber': page,
        'origtext': person['personMetadata']['results']['originalText']
    }

    personModel = Person.create_or_get(**personData)[0]

    if person['spouse'] is not None and person['spouse']['results']['hasSpouse'] is True:
        spouseModel = _populate_spouse(person['spouse']['results'], personModel, person)[0]

    for child in person['children']['results']['children']:
        childModel = _populate_child(child, personModel, person)[0]

    _populate_migration_history(person['migrationHistory']['results']['locations'], personModel)



