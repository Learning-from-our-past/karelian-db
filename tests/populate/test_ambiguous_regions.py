import pytest
from db_management.models.db_siirtokarjalaistentie_models import *

class TestMarkRegionsAmbiguous:

    def should_have_marked_places_with_multiple_regions_in_db_as_ambiguous(self):
        # In test data Hiitola is set up to have both karelia and other regions. This means the
        # Place table should have two Kilpola rows and both should have ambiguousRegion flag set true
        rows = list(Place.select().where(Place.name == 'Hiitola'))

        assert len(rows) == 2
        assert rows[0].ambiguousRegion is True
        assert rows[1].ambiguousRegion is True

