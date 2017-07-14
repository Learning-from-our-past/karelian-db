from peewee_migrate import Router
import material.settings
from models.db_connection import db_connection

# FIXME: Dirty way to pass the schema for migration history so that peewee_migrate will work properly.
# More information: https://github.com/klen/peewee_migrate/issues/51
from peewee_migrate import MigrateHistory
MigrateHistory._meta.schema = 'system'

db_connection.init_database()
db_connection.connect()
database = db_connection.get_database()

router = Router(database)

# Run all unapplied migrations
router.run()
