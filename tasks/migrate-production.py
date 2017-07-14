from peewee_migrate import Router
from playhouse.db_url import connect

# FIXME: Dirty way to pass the schema for migration history so that peewee_migrate will work properly.
# More information: https://github.com/klen/peewee_migrate/issues/51
from peewee_migrate import MigrateHistory
MigrateHistory._meta.schema = 'system'

database = connect('postgresql://postgres@karelia-17.it.helsinki.fi:5432/learning-from-our-past')

router = Router(database)

# Run all unapplied migrations
router.run()
