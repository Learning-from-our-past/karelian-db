from peewee_migrate import Router
from database.db_management.models.db_connection import db_connection
from database.config import CONFIG

db_connection.init_database(db_name=CONFIG['db_name'], db_user=CONFIG['db_admin'])
db_connection.connect()
database = db_connection.get_database()
router = Router(database, schema='system')

# Create migration
router.create('migration_name')