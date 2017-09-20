from database.db_management.models.db_siirtokarjalaistentie_models import *
"""
Try to fill in region and correct name for Places based on their stemmed names.

First get all Places with no region data. Then for each such Place, fetch Places with same
stem with region data. If one such Place is found, use its name and region in current row.
This works since from books we already know for some places their region (based on migration data). Use that
data to fill region data to birthplaces etc.

This will create duplicate rows to db which should be removed later on or rather combined so that both
migration records and birth locations etc. point to same rows.
"""
db_connection.init_database()
db_connection.connect()
database = db_connection.get_database()

q = (Place.select()
     .where(Place.region == None)
     .order_by(Place.name))

count = len(q)
duplicates = []
for place_entry in q:
    existing_places_with_region = Place.select().where(Place.stemmedName == place_entry.stemmedName).where(Place.region != None)
    if len(existing_places_with_region) > 0:
        existing_place = None
        if len(existing_places_with_region) == 1:
            existing_place = existing_places_with_region[0]

            place_entry.name = existing_place.name

            place_entry.region = existing_place.region
            place_entry.save()
        else:
            # All of the places contain same region, so it is safe to get their region info to current place
            regions = list((p.region for p in existing_places_with_region))
            names = list((p.stemmedName for p in existing_places_with_region))

            duplicates.append(place_entry.stemmedName)
            if len(set(regions)) == 1:
                existing_place = existing_places_with_region[0]
                place_entry.name = existing_place.name
                place_entry.region = existing_place.region
                print('combine')
                place_entry.save()

print(list(set(duplicates)))
database.commit()