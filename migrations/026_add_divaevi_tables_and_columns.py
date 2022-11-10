"""Peewee migrations -- 026_add_divaevi_tables_and_columns.py.
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
    DROP SCHEMA IF EXISTS divaevi;
    CREATE SCHEMA divaevi;
    
    CREATE TABLE divaevi."DivaeviPerson"(
      id INTEGER PRIMARY KEY,
      "birthDay" INTEGER,
      "birthMonth" INTEGER,
      "birthYear" INTEGER
    );
    
    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "divaeviId" INTEGER REFERENCES divaevi."DivaeviPerson"(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."divaeviId" is 'A reference to a person in the DivaeviPerson table, used to fetch the data for the person acquired from linking the person to the divaevi database.';
    
    GRANT USAGE ON SCHEMA divaevi to researcher, kaira;
    GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "divaevi"."DivaeviPerson" TO kaira;
    GRANT SELECT, REFERENCES ON "divaevi"."DivaeviPerson" TO researcher;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "divaevi" TO researcher, kaira;
    """)


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""