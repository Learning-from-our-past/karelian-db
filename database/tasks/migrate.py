from peewee_migrate import Router

from common.database_config import CONFIG
from common.db_connection import db_connection

db_connection.init_database(db_name=CONFIG['db_name'], db_user=CONFIG['db_admin'])
db_connection.connect()
database = db_connection.get_database()

router = Router(database, schema='system', migrate_dir='database/migrations')

# Run all unapplied migrations
router.run()
