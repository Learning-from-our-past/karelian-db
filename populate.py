from models.db_siirtokarjalaistentie_models import *
from config import CONFIG
import nltk.stem.snowball as snowball
stemmer = snowball.SnowballStemmer('finnish')

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


def _figure_gender_of_couple(person1, person2):
    if person1.sex == 'm':
        male = person1
        female = person2
    elif person1.sex == 'f':
        male = person2
        female = person1
    else:
        raise SexMissingException

    return {'male': male, 'female': female}


def _populate_place(place):
    """
    When populating new Place to the database, try to figure out if place already exists there either as directly or
    one with slightly different name. Check if there is a place name with same stem as the new place which is going to
    be added.
    :param place:
    :return:
    """

    if place['name'] is None or place['name'] == '':
        return None

    place['stemmedName'] = stemmer.stem(place['name'])

    # Combine places which have same stemmed form of the name
    if CONFIG['place_snowball_stem']:
        existing_places = (Place.select()
                           .where(Place.stemmedName == place['stemmedName']))

        # Check if there is place with same region
        places_with_same_region = [p for p in existing_places
                                   if p.region is not None
                                   and p.region == place['region']]

        if len(places_with_same_region) > 0:
            existing_place = places_with_same_region[0]

            if existing_place.latitude is None or existing_place.longitude is None and place['latitude'] is not None and place['longitude'] is not None:
                # Update coordinates if they are missing from existing record
                existing_place.latitude = place['latitude']
                existing_place.longitude = place['longitude']
                existing_place.location = pft(place['longitude'], place['latitude'])
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


def _populate_spouse(spouse, personModel, person):
    birth_place = _populate_place({
        'name': spouse['birthData']['birthLocation']['results']['locationName'],
        'extractedName': spouse['birthData']['birthLocation']['results']['locationName'],
        'latitude': None,
        'longitude': None,
        'region':  spouse['birthData']['birthLocation']['results']['region'],
        'location': None
    })
    profession = _populate_profession({
        'name': spouse['profession']['results']
    })[0]

    spouseData = {
        'kairaId': spouse['kairaId'],
        'firstName': spouse['spouseName'],
        'lastName': person['name']['results']['surname'],
        'prevLastName': spouse['originalFamily']['results'],
        'sex': _invert_gender(person['name']['results']['gender']),
        'birthDay': spouse['birthData']['results']['birthDay'],
        'birthMonth': spouse['birthData']['results']['birthMonth'],
        'birthYear': spouse['birthData']['results']['birthYear'],
        'primaryPerson': False,
        'birthPlaceId': birth_place,
        'professionId': profession,
        'deathDay': None,
        'deathMonth': None,
        'deathYear': spouse['deathYear']['results'],
        'deathPlaceId': None,
        'ownHouse': None,
        'returnedKarelia': _convert_boolean_none(None), # TODO: Fill in once Spouse data contains information about their personal migration route
        'previousMarriages': _convert_boolean_none(None),  # FIXME: This is missing from new data set.
        'pageNumber': personModel.pageNumber,
        'originalText': personModel.originalText
    }

    return Person.create_or_get(spouseData)

def _populate_marriage(person_model, spouse_model, spouse_entry):
    male = None
    female = None

    if person_model.sex == 'm':
        male = person_model
        female = spouse_model
    elif person_model.sex == 'f':
        male = spouse_model
        female = person_model

    wedding_year = spouse_entry['weddingYear']['results'] or None


    if male and female:
        return Marriage.create(
            manId=male.id,
            womanId=female.id,
            weddingYear=wedding_year)
    else:
        return None


def _populate_child(child, personModel, spouseModel, person):
    location = None
    if child['location']['coordinates']['latitude'] and child['location']['coordinates']['longitude']:
        location = pft(child['location']['coordinates']['latitude'], child['location']['coordinates']['longitude'])

    birth_place = _populate_place({
        'name': child['location']['locationName'],
        'extractedName': child['location']['locationName'],
        'latitude': child['location']['coordinates']['latitude'] or None,
        'longitude': child['location']['coordinates']['longitude'] or None,
        'location': location,
        'region': child['location']['region']
    })

    try:
        parents = _figure_gender_of_couple(personModel, spouseModel)
    except SexMissingException:
        # If parent gender could not be assigned, assume that Person is male.
        parents = {'male': personModel, 'female': None}

    father_id = None
    mother_id = None

    if parents['male']:
        father_id = parents['male'].id

    if parents['female']:
        mother_id = parents['female'].id

    childData = {
        'kairaId': child['kairaId'],
        'firstName': child['name'],
        'lastName': person['name']['results']['surname'],
        'birthYear': child['birthYear'],
        'sex': _transform_sex(child['gender']),
        'birthPlaceId': birth_place,
        'parentPersonId': personModel,
        'fatherId': father_id,
        'motherId': mother_id
    }

    return Child.create_or_get(childData)

def _populate_migration_record(record):
    return Livingrecord.create_or_get(record)

def _populate_migration_history(places, personModel):
    for p in places:
        location = None
        if p['coordinates']['longitude'] and p['coordinates']['latitude']:
            location = pft(p['coordinates']['longitude'], p['coordinates']['latitude'])

        placeModel = _populate_place({
            'name': p['locationName'],
            'extractedName': p['locationName'],
            'latitude': p['coordinates']['latitude'],
            'longitude': p['coordinates']['longitude'],
            'region': p['region'],
            'location': location
        })

        _populate_migration_record({
            'personId': personModel,
            'placeId': placeModel,
            'movedIn':  p['movedIn'],
            'movedOut': p['movedOut']
        })

def _convert_boolean_none(value):
    """
    Convert boolean or None value to string of three different values. Reason being that
    MS Access can't make difference between NULL and False values of boolean field...
    :param value: 
    :return: 
    """
    if value is None:
        return 'unknown'
    elif value is True:
        return 'true'
    else:
        return 'false'

def populate_person(person):
    birth_place = _populate_place({
        'name': person['birthLocation']['results']['locationName'],
        'extractedName': person['birthLocation']['results']['locationName'],
        'latitude': None,
        'longitude': None,
        'region': person['birthLocation']['results']['region'],
        'location': None
    })

    page = _populate_page({
        'pageNumber': person['personMetadata']['results']['approximatePageNumber']
    })[0]

    profession = _populate_profession({
        'name': person['profession']['results']
    })[0]

    personData = {
        'kairaId': person['kairaId']['results'],
        'firstName': person['name']['results']['firstNames'],
        'lastName': person['name']['results']['surname'],
        'prevLastName': person['originalFamily']['results'],
        'sex': _transform_sex(person['name']['results']['gender']),
        'birthDay': person['birthday']['results']['birthDay'],
        'birthMonth': person['birthday']['results']['birthMonth'],
        'birthYear': person['birthday']['results']['birthYear'],
        'birthPlaceId': birth_place,
        'primaryPerson': True,
        'deathDay': None,
        'deathMonth': None,
        'deathYear': None,
        'deathPlaceId': None,
        'ownHouse': person['ownHouse']['results'],
        'professionId': profession,
        'returnedKarelia': _convert_boolean_none(person['migrationHistory']['results']['returnedToKarelia']),
        'previousMarriages': _convert_boolean_none(person['previousMarriagesFlag']['results']),
        'pageNumber': page,
        'originalText': person['personMetadata']['results']['originalText']
    }

    personModel = Person.create_or_get(personData)

    spouseModel = None
    if person['spouse'] is not None and person['spouse']['results']['hasSpouse'] is True:
        spouseModel = _populate_spouse(person['spouse']['results'], personModel, person)
        marriage = _populate_marriage(personModel, spouseModel, person['spouse']['results'])


    for child in person['children']['results']['children']:
        childModel = _populate_child(child, personModel, spouseModel, person)

    _populate_migration_history(person['migrationHistory']['results']['locations'], personModel)


class SexMissingException(Exception):
    pass
