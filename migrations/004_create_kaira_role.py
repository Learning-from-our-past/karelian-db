"""Peewee migrations -- 004_migration_name.py.

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

# Creates user and grants permissions. However, password should be set by admin!
def migrate(migrator, database, fake=False, **kwargs):
    migrator.sql(
        """
        do
        $body$
        declare
          num_users integer;
        begin
           SELECT count(*)
             into num_users
           FROM pg_user
           WHERE usename = 'kaira';
        
           IF num_users = 0 THEN
              CREATE USER kaira;
           END IF;
        end
        $body$;
        
        GRANT USAGE ON SCHEMA "siirtokarjalaisten_tie" TO kaira;
        GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Child" TO kaira;
        GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."LivingRecord" TO kaira;
        GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Marriage" TO kaira;
        GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Page" TO kaira;
        GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Person" TO kaira;
        GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Place" TO kaira;
        GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Profession" TO kaira;
        
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "siirtokarjalaisten_tie" TO kaira;
        """
    )
