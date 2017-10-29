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
