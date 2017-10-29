from invoke import task
import getpass
from database.tasks.migrate import migrate as migrate_backend
from kairatools.backend.tasks.migrate import migrate as migrate_kairatools


@task()
def test(ctx, target):
    """
    Run tests for specified target
    """
    ctx.run('python -m pytest {}'.format(target))


@task()
def test_all(ctx):
    """
    Run tests for both database and kairatools
    """
    test(ctx, 'database')
    test(ctx, 'kairatools/backend')


@task(help={'superuser': 'The database super user which can be used to create and modify the database.'})
def setup(ctx, superuser='postgres'):
    """
    Setup database and run initialization and migrations.
    To avoid repetitive password prompts, it is suggested to have a pgpass-entry for superuser
    used in this task.
    """
    ctx.run("psql -U {} template1 -c 'create extension hstore';".format(superuser))
    ctx.run('createdb -U {} learning-from-our-past'.format(superuser))
    ctx.run('psql -U {} -d learning-from-our-past -a -f database/sql/initial_db.sql'.format(superuser))

    superuser_password = getpass.getpass('Please input password for superuser {}: '.format(superuser))
    migrate_backend(superuser, superuser_password)
    migrate_kairatools(superuser, superuser_password)
    ctx.run('python -m database.tasks.migrate')
    ctx.run('python -m kairatools.backend.tasks.migrate')
