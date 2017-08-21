import nltk.stem.snowball as snowball
from db_management.models.db_siirtokarjalaistentie_models import *
stemmer = snowball.SnowballStemmer('finnish')


def create_migration_history(key, primary_person, migration_history, data_entry, extra_data):
    """
    Update/create the migration history of the person. This process is naive at the moment and will simply update the
    LivingRecords in the db to correspond the records in json. Basically existing records will be deleted if any
    difference is found between existing and new records. THIS PROCESS WILL NOT TAKE IN ACCOUNT MANUAL CHANGES IN THE DB!

    Preserving manual changes would be tricky since it is difficult to reliably compare which records are in the db
    and which are not when there might be manual changes in them. This might be worthwhile later but for now simply
    prevent manual changes to LivingRecords table with db rules and let only Kaira to modify the table.

    """
    def _none(value):
        if value is None:
            return 'none'
        return str(value)

    change_detected = False
    existing_living_records = list(LivingRecord.select().where(LivingRecord.personId == primary_person.id))

    if len(existing_living_records) != len(migration_history):
        change_detected = True
    else:
        existing_living_records_by_key = {stemmer.stem(record.placeId.name) + '_' + _none(record.placeId.region) + '_' + _none(record.movedIn) + '_' + _none(record.movedOut): True for record in existing_living_records}
        new_living_records_keys = [stemmer.stem(location['locationName']) + '_' + _none(location['region']) + '_' + _none(location['movedIn']) + '_' + _none(location['movedOut']) for location in migration_history]

        for key in new_living_records_keys:
            if key not in existing_living_records_by_key:
                change_detected = True
                break

    if change_detected:
        _delete_migration_history(primary_person)

        # Repopulate the migration history back to the db
        for record in migration_history:
            place_model_id = add_place(None, None, record, data_entry, None)[1]

            LivingRecord.create_or_get({
                'personId': primary_person,
                'placeId': place_model_id,
                'movedIn': record['movedIn'],
                'movedOut': record['movedOut']
            })

    return primary_person, None


def _delete_migration_history(primary_person):
    LivingRecord.delete().where(LivingRecord.personId == primary_person.id).execute()


def add_place(key, model, place_data, data_entry, extra_data):
    if place_data is None:
        return model, None

    if 'coordinates' not in place_data:
        latitude, longitude = _get_lat_lon(place_data)
    else:
        latitude, longitude = _get_lat_lon(place_data['coordinates'])

    place_model = _populate_place({
        'name': place_data['locationName'],
        'extractedName': place_data['locationName'],
        'latitude': latitude,
        'longitude': longitude,
        'region': place_data['region'],
        'location': _get_postgis_location({'latitude': latitude, 'longitude': longitude})
    })

    if place_model is None:
        return model, None
    else:
        return model, place_model.id

def _get_lat_lon(collection):
    latitude = None if 'latitude' not in collection else collection['latitude']
    longitude = None if 'longitude' not in collection else collection['longitude']

    return latitude, longitude

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
