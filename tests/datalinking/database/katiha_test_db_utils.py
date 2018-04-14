# Do not log useless messages about migrations during test setup
from db_management.testing.base_test_db_utils import BaseDBUtils
from tests.datalinking.database.katiha_database_test_config import CONFIG
from datalinking.models import katiha_models


class KatihaDBUtils(BaseDBUtils):
    def __init__(self):
        sequences_to_reset = [('public', 'LA_ID_seq'), ('public', 'parishes_id_seq')]
        truncate_schema = 'public'
        super().__init__(CONFIG, sequences_to_reset, truncate_schema)

    def _create_schema(self):
        # Create DB tables from the models
        katiha_models.set_database_to_models(self.peewee_database)
        self.peewee_database.create_table(katiha_models.Parishes)
        self.peewee_database.create_table(katiha_models.La)


KatihaDBUtils = KatihaDBUtils()
