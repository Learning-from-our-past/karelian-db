from invoke import task
import os
import sys
# A slight hack to change the module path to parent directory so that all imports work as expected even when these
# tasks are ran inside database/ directory.
sys.path[0] = '../'

from database.tasks.new_migration import create_migration_file
from database.tasks.migrate import migrate_local, migrate_production


@task()
def test(ctx):
    os.chdir('../')
    ctx.run('python -m pytest database')


@task()
def new_migration(ctx):
    """
    Create a new empty migration file to migrations directory.
    """
    create_migration_file('migrations')


@task(optional=['production'], help={'production': 'If set, runs migrations to the production server instead of local.'})
def migrate(ctx, production=None):
    """
    Run migrations to the database. Default to localhost or production if invoked with option -p.
    """
    if production:
        migrate_production()
    else:
        migrate_local()


@task(optional=['first', 'all_books'], help={
    'first': 'Populate only first book to the database.',
    'all_books': 'Populates all siirtokarjalaisten_tie json files form material/ directory'
})
def populate(ctx, first=None, all_books=None):
    """
    Populate json files in material directory to the database. Either -f or -a
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

    os.chdir('../')
    if first:
        ctx.run('python -m database.main database/material/{}'.format(karelian_books[0]))
    elif all_books:
        for book in karelian_books:
            ctx.run('python -m database.main database/material/{}'.format(book))
    else:
        print('Should provide either [first], or [all] flag on invocation!')
        sys.exit(1)


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
