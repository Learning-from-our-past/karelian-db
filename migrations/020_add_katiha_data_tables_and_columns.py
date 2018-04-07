"""Peewee migrations -- 020_migration_name.py.

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
    DROP SCHEMA IF EXISTS katiha;
    CREATE SCHEMA katiha;

    CREATE TABLE katiha."Family"(
      id INTEGER PRIMARY KEY
    );
    
    CREATE TABLE katiha."Language"(
      id SERIAL PRIMARY KEY,
      language TEXT NOT NULL
    );
    
    CREATE TABLE katiha."KatihaPerson"(
      id INTEGER PRIMARY KEY,
      "familyId" INTEGER REFERENCES katiha."Family"(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
      "motherLanguageId" INTEGER REFERENCES katiha."Language"(id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
      "birthDay" INTEGER,
      "birthMonth" INTEGER,
      "birthYear" INTEGER
    );
    
    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "katihaId" INTEGER REFERENCES katiha."KatihaPerson"(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."katihaId" is 'A reference to a person in the KatihaPerson table, used to fetch the data for the person acquired from linking the person to the Katiha database.';
    
    GRANT USAGE ON SCHEMA katiha to researcher, kaira;
    GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "katiha"."KatihaPerson" TO kaira;
    GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "katiha"."Family" TO kaira;
    GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "katiha"."Language" TO kaira;
    GRANT SELECT, REFERENCES ON "katiha"."Family" TO researcher;
    GRANT SELECT, REFERENCES ON "katiha"."KatihaPerson" TO researcher;
    GRANT SELECT, REFERENCES ON "katiha"."Language" TO researcher;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "katiha" TO researcher, kaira;
    """)


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""
