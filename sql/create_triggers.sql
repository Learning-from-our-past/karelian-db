
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

    for column_name, new_value in TD['new'].items():
        if column_name != 'editLog':
            # Only mark false values to true. If value is missing, it can be safely set.
            if column_name not in edit_log or new_value != TD['old'][column_name]:
                edit_log[column_name] = {
                    'oldValue': TD['old'].get(column_name),
                    'lastChanged': datetime.datetime.utcnow().isoformat(),
                    'author': user
                }

    TD['new']['editLog'] = json.dumps(edit_log)
    return 'MODIFY'
$$ LANGUAGE plpython3u;

CREATE TRIGGER person_log_update_trigger
  BEFORE UPDATE ON "siirtokarjalaisten_tie"."Person"
  FOR EACH ROW
  EXECUTE PROCEDURE log_edits_trigger();
