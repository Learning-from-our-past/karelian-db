import os
from time import sleep
from invoke import task
import getpass
import sys
import psycopg2
from tasks.restore_database import restore_encrypted_backup
from tasks.new_migration import create_migration_file
from tasks.migrate import migrate_local, migrate_production
from datalinking.run_data_linking import run_data_linking


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
        migrate_local(password=os.getenv('LFOP_DB_PASSWORD') or None)


@task()
def new_migration(ctx):
    """
    Create a new empty migration file to migrations directory.
    """
    create_migration_file('migrations')


@task(help={
    'first': 'Populate only first book to the database.',
    'all_books': 'Populates all siirtokarjalaisten_tie json files from material/ directory',
    'data-type': 'Type of data to populate, default "kaira". Specify "link" to populate linked data instead.',
    'port': 'Port to use for the database connection.'
})
def populate(ctx, first=False, file=None, all_books=False, data_type='kaira', port=5432):
    """
    Populate json files in material directory to the database. -d has to be provided to specify
    data type, then either -f, or -a has to be specified in the case of "-d kaira". If one of them
    is not specified, -i should be specified. With "-d link", -i should be specified.
    """
    # TODO: Maybe support providing a relative path to any file? However, note the slightly strange path, since working
    # directory is changed to parent directory...
    karelian_books = [
        'siirtokarjalaiset_I.json',
        'siirtokarjalaiset_II.json',
        'siirtokarjalaiset_III.json',
        'siirtokarjalaiset_IV.json',
    ]

    if data_type == 'kaira':
        if first:
            ctx.run(
                'python -m main -t kaira material/{} -p {}'.format(karelian_books[0], port))
        elif all_books:
            for book in karelian_books:
                ctx.run(
                    'python -m main -t kaira material/{} -p {}'.format(book, port))
        elif file:
            ctx.run('python -m main -t kaira {} -p {}'.format(file, port))
        else:
            print(
                'Should provide either [file], or [first] or [all-books] flag on invocation!')
            sys.exit(1)
    elif data_type == 'link':
        if file:
            ctx.run('python -m main -t link {} -p {}'.format(file, port))
        else:
            print('Should provide [file] on invocation!')
            sys.exit(1)
    else:
        print('Should provide [data-type] on invocation!')
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
    ctx.run('python -m pytest tests --ignore .direnv')


def _setup_database(ctx, superuser, port=5432):
    ctx.run(
        'createdb -h localhost -U {} learning-from-our-past -p {}'.format(superuser, port))
    ctx.run('psql -h localhost -U {} -d learning-from-our-past -p {} -a -f sql/initial_db.sql'.format(superuser, port))

    superuser_password = getpass.getpass(
        'Please input password for superuser {}: '.format(superuser))
    migrate_local(superuser, superuser_password,
                  migration_dir='migrations', port=port)


@task(help={'superuser': 'The database super user which can be used to create and modify the database.'})
def setup(ctx, superuser='postgres'):
    """
    Setup database and run initialization and migrations.
    To avoid repetitive password prompts, it is suggested to have a pgpass-entry for superuser
    used in this task.
    """
    _setup_database(ctx, superuser)


@task(help={'superuser': 'The database super user which can be used to create and modify the database.',
            'port': 'The port to connect to the database on.'})
def recreate_db(ctx, superuser='postgres', port=5432):
    """
    Drops the existing database and recreates it from scratch.
    """
    ctx.run(
        'dropdb -U {} -p {} -h localhost learning-from-our-past'.format(superuser, port))
    _setup_database(ctx, superuser, port)


@task(help={
    'superuser': 'The database super user which can be used to create and modify the database.',
    'dumpfile': 'Path to the encrypted dump file to be restored.',
    'sslkey': 'Path to the SSL private key for decrypting the backup file.',
    'port': 'Port to use for DB connection.'
})
def restore_backup(ctx, dumpfile, sslkey, superuser='postgres', port=5432):
    """
    Restore encrypted database backup snapshot.
    """
    restore_encrypted_backup(superuser, dumpfile, sslkey, port)


@task(help={
    'output_path': 'The path under which to store the linked data.'
})
def link_data(ctx, output_path='./material/'):
    """
    Link MiKARELIA data to Katiha data and dump the results of the data linking to the hard drive.
    """
    run_data_linking(output_path)


@task(help={
    'port': 'The localhost port which is used to connect to the database. Defaults to 5432',
    'db-password': 'Password for db superuser'
})
def docker_db_setup(ctx, port=os.getenv('DB_PORT') or 5432, db_password=os.getenv('LFOP_DB_PASSWORD') or None):
    """
    Setup the database using Docker with all the required Postgres extensions preinstalled.
    """
    if db_password is None:
        print('Set env var LFOP_DB_PASSWORD')
        return -1
    print('Installing the development database using Docker...')
    ctx.run('sudo docker build -t lfop-db docker')
    ctx.run('sudo docker -e POSTGRES_PASSWORD={} run -p {}:5432 -d --name=lfop-db-container lfop-db'.format(db_password, port))

    # A silly wait for Postgres to finish startup in the Docker container before running migrations.
    print('Waiting for Postgres to finish startup operations...')
    while True:
        try:
            conn = psycopg2.connect(
                user='postgres', host='localhost', connect_timeout=1, port=port)
            conn.close()
            break
        except:
            sleep(0.1)

    print('Creating the database and running migrations...')
    _setup_database(ctx, 'postgres', port)

    print('Finished. The database is ready for development and running on localhost:{}'.format(port))
    print('Please add the following value to your .env file: export DB_PORT={}'.format(port))


@task()
def docker_db_start(ctx):
    """
    Start the Docker container with the Postgres database. The container should first be installed with
    the docker-db-setup command.
    """
    ctx.run('sudo docker start lfop-db-container')


@task()
def docker_db_stop(ctx):
    """
    Stop the Docker container with the Postgres database.
    """
    ctx.run('sudo docker stop lfop-db-container')


@task()
def docker_db_destroy(ctx):
    """
    Destroy the Docker container. After this you can install it again with docker-db-setup command.
    """
    ctx.run('sudo docker stop lfop-db-container')
    ctx.run('sudo docker rm lfop-db-container')
    ctx.run('sudo docker rmi lfop-db')
