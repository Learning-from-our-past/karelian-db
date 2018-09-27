import os

CONFIG = {
  'drop_database_on_init': True,
  'master_db': 'postgres',
  'test_db_name': 'katiha_testdb',
  'db_admin': os.getenv('DB_ADMIN_NAME') or 'postgres',
  'db_user': 'kaira',
  'db_port': os.getenv('DB_PORT') or 5432,
  'sql_files': [
    './tests/datalinking/database/test_users.sql'
  ],
}
