from common.siirtokarjalaistentie_models import *
"""
Minor helper function which tries to find Places which have multiple rows with same name
but different region entry (other, karelia, NULL) and adds flag for these places so that
in data analysis it would be easier to detect places which might have wrong region.
"""


def mark_ambiguous_places(database):
    with database.atomic():
        q = (Place.select()
             .order_by(Place.name))

        for place_entry in q:
            existing_places_with_region = Place.select().where(Place.stemmedName == place_entry.stemmedName).where(Place.region != None)
            if len(existing_places_with_region) > 1:
                # Mark this place as ambiguous meaning that it has multiple region records (duplicates in db) and therefore
                # it likely has different region entries for each entry.
                place_entry.ambiguousRegion = True
                place_entry.save()

    database.commit()
