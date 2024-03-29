import os
import sys
import getpass
from tasks.migrate import migrate_local as run_db_migrations

"""
This is utility script for restoring encrypted backup files to the database. Script should be called
with top level karelian-db as working directory. This can be done with makefile task restore-backup.

The script first asks the location of the backup and SSL-private key for decrypting it. If decryption 
is ok, the postgres superuser name is asked for running the database commands. Superuser should be someone
which you can authenticate with password or via peer auth.

Rest of the script drops the current database, reinitializes it and then restores the backup.
"""


class TerminalColors:
    WARNING = '\033[93m'
    ENDC = '\033[0m'


def restore_encrypted_backup(superuser, dump_path, ssl_key_path, port):
    print('Preparing to restore existing database backup dump. Dump should contain schemas "siirtokarjalaisten_tie"'
          ' and "system".')
    print('For reliable results, {} please check that there is no active connections to the database before '
          'continuing.{}'.format(TerminalColors.WARNING, TerminalColors.ENDC))

    if not os.path.isfile(dump_path):
        print('Error, provided path is not a valid file.')
        sys.exit(1)

    if not os.path.isfile(ssl_key_path):
        print('Error, provided path to the SSL-key is not valid.')
        sys.exit(1)

    # Decrypt the backup file before restore
    decrypt_command = 'openssl smime -decrypt -in {} -binary -inform SMIME -inkey {} -out learning-from-our-past-dump'\
        .format(dump_path, ssl_key_path)
    os.system(decrypt_command)

    # This is needed to cleanup the decrypted file after we are finished.
    decrypted_backup_path = os.path.join(os.getcwd(), 'learning-from-our-past-dump')

    if not os.path.isfile(decrypted_backup_path):
        print('Decrypting the backup failed, there is no file in path', decrypted_backup_path)
        sys.exit(1)

    print('Before database restore, the current database has to be reinitialized. {} '
          'This WILL wipe out the existing data!{}'.format(TerminalColors.WARNING, TerminalColors.ENDC))
    proceed_answer = None

    while proceed_answer != 'yes' and proceed_answer != 'no':
        proceed_answer = input('yes/no:')

    if proceed_answer == 'no':
        os.remove(decrypted_backup_path)
        sys.exit(0)

    # Recreate the database by dropping and reinitializing it.
    drop_cmd = 'dropdb -U {} -h localhost -p {} learning-from-our-past'.format(superuser, port)
    print(drop_cmd, os.system(drop_cmd))

    create_cmd = 'createdb -U {} -h localhost -p {} learning-from-our-past'.format(superuser, port)
    print(create_cmd, os.system(create_cmd))

    init_cmd = 'psql -U {} -h localhost -p {} -d learning-from-our-past -a -f sql/initial_db.sql'.format(superuser, port)
    print(init_cmd, os.system(init_cmd))

    print('Ready to run the migrations')
    database_password = getpass.getpass('Please input password for user {}: '.format(superuser))
    run_db_migrations(superuser, database_password, migration_dir='migrations', port=port)

    print('Database reinitialized successfully!')

    # Restore
    print('Restoring data...')
    restore_cmd = 'pg_restore -U {} -h localhost -p {} -c --if-exists -d learning-from-our-past {}'.format(superuser, port, decrypted_backup_path)
    print(restore_cmd, os.system(restore_cmd))

    print('Database restoring finished. {} Please check the printed logs and '
          'verify that the population of new data from Kaira still works ok after the restore. Remember also to '
          'delete your private key if necessary! {}'.format(TerminalColors.WARNING, TerminalColors.ENDC))

    os.remove(decrypted_backup_path)
