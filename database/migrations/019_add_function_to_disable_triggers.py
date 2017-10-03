"""Peewee migrations -- 019_migration_name.py.

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
    """Write your migrations here."""
    migrator.sql("""
    /* Enable/disable all triggers in siirtokarjalaisten_tie schema */
    CREATE OR REPLACE FUNCTION enable_triggers(DoEnable boolean) RETURNS void AS
    $$
    DECLARE
    mytables CURSOR FOR
        SELECT n.nspname, *
        FROM pg_class
          JOIN pg_catalog.pg_namespace n ON n.oid = pg_class.relnamespace
        WHERE relhastriggers is TRUE AND nspname = 'siirtokarjalaisten_tie';
    BEGIN
      FOR mt IN mytables LOOP
        IF DoEnable THEN
          EXECUTE 'ALTER TABLE ' || quote_ident('siirtokarjalaisten_tie') || '.' || quote_ident(mt.relname) || ' ENABLE TRIGGER ALL';
        ELSE
          EXECUTE 'ALTER TABLE ' || quote_ident('siirtokarjalaisten_tie') || '.' || quote_ident(mt.relname) || ' DISABLE TRIGGER ALL';
        END IF;
      END LOOP;
    END;
    $$
    LANGUAGE 'plpgsql';
    
    -- Delete old audit logs since they are polluted by kaira update logs
    delete from audit.logged_actions;
    
    -- Give Kaira a permission to disable and enable triggers
    ALTER FUNCTION enable_triggers(DoEnable boolean) OWNER TO kaira;
    """)



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

