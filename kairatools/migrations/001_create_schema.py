"""Peewee migrations -- 001_migration_name.py.

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
    migrator.sql(
        """
        DROP SCHEMA IF EXISTS kairatools CASCADE;
        CREATE SCHEMA kairatools;
        
        CREATE TABLE kairatools."User"(
          id SERIAL PRIMARY KEY,
          email TEXT NOT NULL UNIQUE,
          password TEXT NOT NULL,
          name TEXT,
          picture TEXT,
          active BOOLEAN DEFAULT FALSE,
          confirmed_at TIMESTAMP DEFAULT NULL,
          last_login_at TIMESTAMP,
          current_login_at TIMESTAMP,
          last_login_ip TEXT,
          current_login_ip TEXT,
          login_count INTEGER DEFAULT 0
        );
        
        CREATE TABLE kairatools."Role" (
          "id" SERIAL PRIMARY KEY,
          "name" TEXT UNIQUE,
          "description" TEXT
        );
        
        CREATE TABLE kairatools."UserRole" (
          id SERIAL PRIMARY KEY,
          "user_id" INTEGER REFERENCES kairatools."User"(id),
          "role_id" INTEGER REFERENCES kairatools."Role"(id)
        );
        
        INSERT INTO kairatools."Role" (name, description) VALUES ('superuser', 'Admin rights. Able to confirm registrations.');
        INSERT INTO kairatools."Role" (name, description) VALUES ('researcher', 'Editing and viewing rights for all tools.');
        
        CREATE TABLE kairatools."migratehistory" (
          id SERIAL PRIMARY KEY,
          "name" TEXT,
          "migrated_at" TIMESTAMP
        );
        """
    )



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

