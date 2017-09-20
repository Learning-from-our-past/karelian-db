from peewee_migrate import Router
from models.db_connection import db_connection


db_connection.init_database('learning-from-our-past', 'postgres')
db_connection.connect()
database = db_connection.get_database()

router = Router(database, schema='kairatools')

# Run all unapplied migrations
router.run()
