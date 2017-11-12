import os

CONFIG = {
  'drop_database_on_init': True,
  'master_db': 'postgres',
  'test_db_name': 'karelian_testdb',
  'admin_user': os.getenv('DB_ADMIN_NAME') or 'postgres',
  'db_user': 'kaira',
  'sql_files': [
    './database/sql/initial_db.sql',
    './database/tests/test_users.sql'
  ],
  'database_migration_path': 'database/migrations',
  'kairatools_migration_path': 'kairatools/backend/migrations'
}