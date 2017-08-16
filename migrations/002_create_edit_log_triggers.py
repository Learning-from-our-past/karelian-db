"""Peewee migrations -- 002_migration_name.py.

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
        -- Trigger function to add JSONB data concerning the changes made to the table.
        -- Records previous value and user who did the change. This way when Kaira does updates,
        -- it can check if the field was edited by human, and not override manual change.
        CREATE OR REPLACE FUNCTION log_edits_trigger()
          RETURNS trigger
        AS $$
            import datetime
            import json
        
            user = plpy.execute('select current_user')[0]['current_user']
            edit_log = json.loads(TD['old']['editLog'])
            last_changed = datetime.datetime.utcnow().isoformat()
        
            for column_name, new_value in TD['new'].items():
                if column_name != 'editLog':
                    # Only mark false values to true. If value is missing, it can be safely set.
                    if column_name not in edit_log or new_value != TD['old'].get(column_name):
                        edit_log[column_name] = {
                            'oldValue': TD['old'].get(column_name),
                            'lastChanged': last_changed,
                            'author': user
                        }
        
            TD['new']['editLog'] = json.dumps(edit_log)
            return 'MODIFY'
        $$ LANGUAGE plpython3u;
        
        -- Set proper starting values for editLog when row is added first time
        CREATE OR REPLACE FUNCTION initialize_log_on_insert_trigger()
          RETURNS trigger
        AS $$
            import datetime
            import json
        
            user = plpy.execute('select current_user')[0]['current_user']
            last_changed = datetime.datetime.utcnow().isoformat()
            edit_log = {}
        
            for column_name, new_value in TD['new'].items():
                if column_name != 'editLog':
                    edit_log[column_name] = {
                        'oldValue': None,
                        'lastChanged': last_changed,
                        'author': user
                    }
        
            TD['new']['editLog'] = json.dumps(edit_log)
            return 'MODIFY'
        $$ LANGUAGE plpython3u;
        
        CREATE TRIGGER person_log_update_trigger
          BEFORE UPDATE ON "siirtokarjalaisten_tie"."Person"
          FOR EACH ROW
          EXECUTE PROCEDURE log_edits_trigger();
        
        CREATE TRIGGER person_insert_trigger
          BEFORE INSERT ON "siirtokarjalaisten_tie"."Person"
          FOR EACH ROW
          EXECUTE PROCEDURE initialize_log_on_insert_trigger();
        
        CREATE TRIGGER child_log_update_trigger
          BEFORE UPDATE ON "siirtokarjalaisten_tie"."Child"
          FOR EACH ROW
          EXECUTE PROCEDURE log_edits_trigger();
        
        CREATE TRIGGER child_insert_trigger
          BEFORE INSERT ON "siirtokarjalaisten_tie"."Child"
          FOR EACH ROW
          EXECUTE PROCEDURE initialize_log_on_insert_trigger();
        
        CREATE TRIGGER place_log_update_trigger
          BEFORE UPDATE ON "siirtokarjalaisten_tie"."Place"
          FOR EACH ROW
          EXECUTE PROCEDURE log_edits_trigger();
        
        CREATE TRIGGER place_insert_trigger
          BEFORE INSERT ON "siirtokarjalaisten_tie"."Place"
          FOR EACH ROW
          EXECUTE PROCEDURE initialize_log_on_insert_trigger();
        
        CREATE TRIGGER living_record_log_update_trigger
          BEFORE UPDATE ON "siirtokarjalaisten_tie"."LivingRecord"
          FOR EACH ROW
          EXECUTE PROCEDURE log_edits_trigger();
        
        CREATE TRIGGER living_record_insert_trigger
          BEFORE INSERT ON "siirtokarjalaisten_tie"."LivingRecord"
          FOR EACH ROW
          EXECUTE PROCEDURE initialize_log_on_insert_trigger();
        
        CREATE TRIGGER profession_log_update_trigger
          BEFORE UPDATE ON "siirtokarjalaisten_tie"."Profession"
          FOR EACH ROW
          EXECUTE PROCEDURE log_edits_trigger();
        
        CREATE TRIGGER profession_insert_trigger
          BEFORE INSERT ON "siirtokarjalaisten_tie"."Profession"
          FOR EACH ROW
          EXECUTE PROCEDURE initialize_log_on_insert_trigger();
        
        CREATE TRIGGER marriage_log_update_trigger
          BEFORE UPDATE ON "siirtokarjalaisten_tie"."Marriage"
          FOR EACH ROW
          EXECUTE PROCEDURE log_edits_trigger();
        
        CREATE TRIGGER marriage_insert_trigger
          BEFORE INSERT ON "siirtokarjalaisten_tie"."Marriage"
          FOR EACH ROW
          EXECUTE PROCEDURE initialize_log_on_insert_trigger();
        """
    )

