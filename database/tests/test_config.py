CONFIG = {
  "drop_database_on_init": True,
  "master_db": "postgres",
  "test_db_name": "karelian_testdb",
  "admin_user": "postgres",
  "db_user": "kaira",
  "db_admin_user": "postgres",
  "sql_files": [
    "./database/sql/initial_db.sql",
    "./database/tests/test_users.sql"
  ]
}