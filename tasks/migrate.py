from peewee_migrate import Router

from common.database_config import CONFIG
from common.db_connection import db_connection
from playhouse.db_url import connect


def migrate_local(superuser=None, password=None, migration_dir='migrations'):
    db_connection.init_database(db_name=CONFIG['db_name'], db_user=superuser or CONFIG['db_admin'], password=password)
    db_connection.connect()
    database = db_connection.get_database()

    router = Router(database, schema='system', migrate_dir=migration_dir)

    # Run all unapplied migrations
    router.run()
    database.close()


def migrate_production(superuser='postgres', migration_dir='migrations'):
    database = connect('postgresql://{}@karelia-17.it.helsinki.fi:5432/learning-from-our-past'.format(superuser))
    router = Router(database, schema='system', migrate_dir=migration_dir)

    # Run all unapplied migrations
    router.run()


if __name__ == '__main__':
    migrate_local()
