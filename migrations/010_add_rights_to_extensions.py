"""Peewee migrations -- 010_migration_name.py.

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
        GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA "extensions" TO public;
        GRANT USAGE ON SCHEMA "extensions" TO public;
        GRANT USAGE ON SCHEMA "audit" TO researcher, kaira;
        GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA "audit" TO researcher, kaira;
        grant usage, select on all sequences in schema "audit" to researcher, kaira;
        GRANT SELECT, INSERT ON TABLE audit.logged_actions to researcher, kaira;
        """
    )



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

