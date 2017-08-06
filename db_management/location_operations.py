from peewee import *
from db_management.models.db_siirtokarjalaistentie_models import *
import nltk.stem.snowball as snowball
stemmer = snowball.SnowballStemmer('finnish')


def add_place(key, model, field_value, data_entry):
    if field_value is None:
        return model, None

    latitude = None if 'latitude' not in field_value else field_value['latitude']
    longitude = None if 'longitude' not in field_value else field_value['longitude']

    place_model = _populate_place({
        'name': field_value['locationName'],
        'extractedName': field_value['locationName'],
        'latitude': latitude,
        'longitude': longitude,
        'region': field_value['region'],
        'location': _get_postgis_location({'latitude': latitude, 'longitude': longitude})
    })

    return model, place_model.id


def _get_postgis_location(coordinates):
    if coordinates['longitude'] and coordinates['latitude']:
        return pft(coordinates['longitude'], coordinates['latitude'])
    else:
        return None


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