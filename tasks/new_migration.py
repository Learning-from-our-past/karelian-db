from peewee_migrate import Router
import sys
sys.path.append('./')  # Hacky way to fix imports
from db_management.database_config import CONFIG
from db_management.db_connection import db_connection


def create_migration_file(migration_dir):
    db_connection.init_database(db_name=CONFIG['db_name'], db_user=CONFIG['db_admin'])
    db_connection.connect()
    database = db_connection.get_database()
    router = Router(database, schema='system', migrate_dir=migration_dir)

    # Create migration
    router.create('migration_name')
