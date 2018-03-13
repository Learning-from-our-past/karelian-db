from invoke import task
import getpass
import sys
from tasks.restore_database import restore_encrypted_backup
from tasks.new_migration import create_migration_file
from tasks.migrate import migrate_local, migrate_production


@task(help={
    'superuser': 'Database superuser name.',
    'database': 'Target database to kill connections from. Defaults to karelian_testdb'
})
def kill_connections(ctx, superuser='postgres', database='karelian_testdb'):
    """
    Kills possible open connections to the target database. Sometimes db tests might leave connections hanging
    preventing then dropping the database. This task can be used to kill connections forcefully. Should not be used in
    production environment.
    """
    ctx.run(""" psql -U {0} -d {1} -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{1}' AND pid <> pg_backend_pid();" """.format(superuser, database))


@task(optional=['production'], help={'production': 'If set, runs migrations to the production server instead of local.'})
def migrate(ctx, production=None):
    """
    Run migrations to the database. Default to localhost or production if invoked with option -p.
    """
    if production:
        migrate_production()
    else:
        migrate_local()


@task()
def new_migration(ctx):
    """
    Create a new empty migration file to migrations directory.
    """
    create_migration_file('migrations')


@task(optional=['first', 'all_books'], help={
    'first': 'Populate only first book to the database.',
    'all_books': 'Populates all siirtokarjalaisten_tie json files from material/ directory',
    'book': 'Populates book in provided path which is located under database/ directory'
})
def populate(ctx, first=None, all_books=None, book=None):
    """
    Populate json files in material directory to the database. Either -f, -b or -a
    arguments should be provided.
    """
    # TODO: Maybe support providing a relative path to any file? However, note the slightly strange path, since working
    # directory is changed to parent directory...
    karelian_books = [
        'siirtokarjalaiset_I.json',
        'siirtokarjalaiset_II.json',
        'siirtokarjalaiset_III.json',
        'siirtokarjalaiset_IV.json',
    ]

    if first:
        ctx.run('python -m main database/material/{}'.format(karelian_books[0]))
    elif all_books:
        for book in karelian_books:
            ctx.run('python -m main database/material/{}'.format(book))
    elif book:
        ctx.run('python -m main database/{}'.format(book))
    else:
        print('Should provide either [first], [book] or [all] flag on invocation!')
        sys.exit(1)


@task(help={
    'config': 'Powa web config file path. Config file can be defined by inserting a secret cookie to .powa_template.conf and renaming the file to .powa-web.conf'
})
def powa_web(ctx, config='.powa-web.conf'):
    """
    Start the powa database monitoring web-client.
    """
    print('Starting powa-web client to localhost:8888 ...')
    ctx.run('powa-web --config=.powa-web.conf')


@task()
def purge_pyc(ctx):
    """
    Remove all .pyc files from the project. Useful after reorganizing the project when tests refuse
    to run because of obsolete pyc-files.
    """
    ctx.run('find . -name "*.pyc" -exec rm -f {} \;')


@task()
def test(ctx):
    """
    Run tests for database
    """
    ctx.run('python -m pytest tests')


def _setup_database(ctx, superuser):
    ctx.run('createdb -U {} learning-from-our-past'.format(superuser))
    ctx.run('psql -U {} -d learning-from-our-past -a -f sql/initial_db.sql'.format(superuser))

    superuser_password = getpass.getpass('Please input password for superuser {}: '.format(superuser))
    migrate_local(superuser, superuser_password, migration_dir='migrations')


@task(help={'superuser': 'The database super user which can be used to create and modify the database.'})
def setup(ctx, superuser='postgres'):
    """
    Setup database and run initialization and migrations.
    To avoid repetitive password prompts, it is suggested to have a pgpass-entry for superuser
    used in this task.
    """
    _setup_database(ctx, superuser)


@task(help={'superuser': 'The database super user which can be used to create and modify the database.'})
def recreate_db(ctx, superuser='postgres'):
    """
    Drops the existing database and recreates it from scratch.
    """
    ctx.run('dropdb -U {} learning-from-our-past'.format(superuser))
    _setup_database(ctx, superuser)


@task(help={
    'superuser': 'The database super user which can be used to create and modify the database.',
    'dumpfile': 'Path to the encrypted dump file to be restored.',
    'sslkey': 'Path to the SSL private key for decrypting the backup file.'
})
def restore_backup(ctx, dumpfile, sslkey, superuser='postgres'):
    """
    Restore encrypted database backup snapshot.
    """
    restore_encrypted_backup(superuser, dumpfile, sslkey)
