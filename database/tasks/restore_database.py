import os.path
import sys

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


print('Preparing to restore existing database backup dump. Dump should contain schemas "siirtokarjalaisten_tie", '
      '"kairatools" and "system".')
print('For reliable results, {} please check that there is no active connections to the database before '
      'continuing.{}'.format(TerminalColors.WARNING, TerminalColors.ENDC))
print('Please provide path to the encrypted backup file:')

dump_path = input('Full path to dump file:')
if not os.path.isfile(dump_path):
    print('Error, provided path is not a valid file.')
    sys.exit(1)

print('The database dump is encrypted. Please provide a full path to private SSL-key:')
ssl_key_path = input()

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
superuser = input('Please input superuser name for Postgres database:')

drop_cmd = 'dropdb -U {} learning-from-our-past'.format(superuser)
print(drop_cmd, os.system('dropdb -U {} learning-from-our-past'.format(superuser)))

create_cmd = 'createdb -U {} learning-from-our-past'.format(superuser)
print(create_cmd, os.system(create_cmd))

init_cmd = 'psql -U {} -d learning-from-our-past -a -f database/sql/initial_db.sql'.format(superuser)
print(init_cmd, os.system(init_cmd))

migrate_db_cmd = 'python -m database.tasks.migrate'
print(migrate_db_cmd, os.system(migrate_db_cmd))

print('Database reinitialized successfully!')

# Restore
restore_cmd = 'pg_restore -U {} -c --if-exists -d learning-from-our-past {}'.format(superuser, decrypted_backup_path)
print(restore_cmd, os.system(restore_cmd))

print('Database restoring finished. {} Please check the printed logs and '
      'verify that the population of new data from Kaira still works ok after the restore. Remember also to '
      'delete your private key if necessary! {}'.format(TerminalColors.WARNING, TerminalColors.ENDC))

os.remove(decrypted_backup_path)
