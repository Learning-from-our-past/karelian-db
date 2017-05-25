import material.settings
from models.db_siirtokarjalaistentie_models import *
"""
Minor helper script which tries to find Places which have multiple rows with same name
but different region entry (other, karelia, NULL) and adds flag for these places so that
in data analysis it would be easier to detect places which might have wrong region.
"""
db_connection.init_database()
db_connection.connect()
database = db_connection.get_database()

q = (Place.select()
     .order_by(Place.name))

count = len(q)
duplicates = []
for place_entry in q:
    existing_places_with_region = Place.select().where(Place.stemmedName == place_entry.stemmedName).where(Place.region != None)
    if len(existing_places_with_region) > 0:
        existing_place = None
        if len(existing_places_with_region) > 1:
            regions = list((p.region for p in existing_places_with_region))
            names = list((p.stemmedName for p in existing_places_with_region))

            duplicates.append(place_entry.stemmedName)

            # Mark this place as ambiguous meaning that it has multiple region records (duplicates in db) and therefore
            # it likely has different region entries for each entry.
            place_entry.ambiguousRegion = True
            place_entry.save()

print('Places with duplicate stemmed name rows:', list(set(duplicates)))
database.commit()