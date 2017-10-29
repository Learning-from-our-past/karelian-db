from invoke import task
import getpass
from database.tasks.migrate import migrate as migrate_backend
from kairatools.backend.tasks.migrate import migrate as migrate_kairatools
from database.tasks.restore_database import restore_encrypted_backup


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


def _setup_database(ctx, superuser):
    ctx.run('createdb -U {} learning-from-our-past'.format(superuser))
    ctx.run('psql -U {} -d learning-from-our-past -a -f database/sql/initial_db.sql'.format(superuser))

    superuser_password = getpass.getpass('Please input password for superuser {}: '.format(superuser))
    migrate_backend(superuser, superuser_password)
    migrate_kairatools(superuser, superuser_password)
    ctx.run('python -m database.tasks.migrate')
    ctx.run('python -m kairatools.backend.tasks.migrate')


@task(help={'superuser': 'The database super user which can be used to create and modify the database.'})
def setup(ctx, superuser='postgres'):
    """
    Setup database and run initialization and migrations.
    To avoid repetitive password prompts, it is suggested to have a pgpass-entry for superuser
    used in this task.
    """
    ctx.run("psql -U {} template1 -c 'create extension hstore';".format(superuser))
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
