
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
            # Only modify changed values. If value is missing, it can be safely set.
            if column_name not in edit_log or new_value != TD['old'][column_name]:
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