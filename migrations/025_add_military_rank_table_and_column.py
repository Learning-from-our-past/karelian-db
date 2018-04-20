"""Peewee migrations -- 025_migration_name.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw


def migrate(migrator, database, fake=False, **kwargs):
    migrator.sql("""
    CREATE TABLE siirtokarjalaisten_tie."MilitaryRank"(
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      "editLog" JSONB NOT NULL DEFAULT '{}'
    );
          
    CREATE TRIGGER militaryrank_log_update_trigger
      BEFORE UPDATE ON "siirtokarjalaisten_tie"."MilitaryRank"
      FOR EACH ROW
      EXECUTE PROCEDURE log_edits_trigger();
    
    CREATE TRIGGER militaryrank_insert_trigger
      BEFORE INSERT ON "siirtokarjalaisten_tie"."MilitaryRank"
      FOR EACH ROW
      EXECUTE PROCEDURE initialize_log_on_insert_trigger();
      
    ALTER TABLE siirtokarjalaisten_tie."Person" 
      ADD COLUMN "militaryRankId" INTEGER REFERENCES siirtokarjalaisten_tie."MilitaryRank"(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL;
      
    GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."MilitaryRank" TO kaira;  
    GRANT SELECT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."MilitaryRank" TO researcher;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "siirtokarjalaisten_tie" TO researcher, kaira;
    """)


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""
