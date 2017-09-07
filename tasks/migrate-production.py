from peewee_migrate import Router
from playhouse.db_url import connect

database = connect('postgresql://postgres@karelia-17.it.helsinki.fi:5432/learning-from-our-past')

router = Router(database, schema='system')

# Run all unapplied migrations
router.run()
