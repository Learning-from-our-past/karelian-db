from peewee_migrate import Router
from common.db_connection import db_connection


def migrate(superuser=None, password=None):
    db_connection.init_database('learning-from-our-past', superuser or 'postgres', password=password)
    db_connection.connect()
    database = db_connection.get_database()

    router = Router(database, schema='kairatools', migrate_dir='kairatools/migrations')

    # Run all unapplied migrations
    router.run()

    database.close()


if __name__ == '__main__':
    migrate()
