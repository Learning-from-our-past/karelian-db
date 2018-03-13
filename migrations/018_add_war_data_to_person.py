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
    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "lotta" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."lotta" is 'Whether the source text contains mention of person having participated in lotta activities.';

    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "servedDuringWar" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."servedDuringWar" is 'Whether the source text contains mention of person having served during the continuation war or the winter war.';

    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "injuredInWar" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."injuredInWar" is 'Whether the source text contains mention of person having been injured in a war.';
    """)



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

