from peewee_migrate import Router

from db_management.models.db_connection import db_connection

db_connection.init_database()
db_connection.connect()
database = db_connection.get_database()
router = Router(database)

# Create migration
router.create('migration_name')