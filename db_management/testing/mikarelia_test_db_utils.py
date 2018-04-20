# Do not log useless messages about migrations during test setup
import logging
from peewee_migrate import LOGGER
from peewee_migrate import Router
from db_management.testing.database_test_config import CONFIG
from db_management.testing.base_test_db_utils import BaseDBUtils

LOGGER.setLevel(logging.WARN)


class MiKARELIADBUtils(BaseDBUtils):
    def __init__(self):
        sequences_to_reset = [('siirtokarjalaisten_tie', 'Child_id_seq'),
                              ('siirtokarjalaisten_tie', 'LivingRecord_id_seq'),
                              ('siirtokarjalaisten_tie', 'Marriage_id_seq'),
                              ('siirtokarjalaisten_tie', 'Person_id_seq'),
                              ('siirtokarjalaisten_tie', 'Place_id_seq'),
                              ('siirtokarjalaisten_tie', 'Profession_id_seq'),
                              ('siirtokarjalaisten_tie', 'MilitaryRank_id_seq'),
                              ('katiha', 'Language_id_seq'),
                              ('system', 'migratehistory_id_seq')]
        truncate_schemas = ('siirtokarjalaisten_tie', 'katiha')
        super().__init__(CONFIG, sequences_to_reset, truncate_schemas)

    def _create_schema(self):
        # Run all unapplied database migrations
        router = Router(self.peewee_database, schema='system', migrate_dir=CONFIG['database_migration_path'])
        router.run()

    def truncate_db(self):
        super().truncate_db()
        self.test_db_connection.cursor().execute('TRUNCATE TABLE system."KairaUpdateReport"')


MiKARELIADBUtils = MiKARELIADBUtils()
