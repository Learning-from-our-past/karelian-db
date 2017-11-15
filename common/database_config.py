import os

CONFIG = {
  "place_snowball_stem": True,
  "anonymize": True,
  "db_user": "kaira",
  "db_admin": os.getenv("DB_ADMIN_NAME") or "postgres",
  "db_name": "learning-from-our-past",
  "users_whose_edits_can_be_overridden": ["kaira"]  # Changes made by these users will not be preserved in the db
}
