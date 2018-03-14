import os

CONFIG = {
  'drop_database_on_init': True,
  'master_db': 'postgres',
  'test_db_name': 'karelian_testdb',
  'db_admin': os.getenv('DB_ADMIN_NAME') or 'postgres',
  'db_user': 'kaira',
  'sql_files': [
    './sql/initial_db.sql',
    './tests/test_users.sql'
  ],
  'database_migration_path': 'migrations'
}