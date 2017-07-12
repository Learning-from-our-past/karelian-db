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
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Child" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."LivingRecord" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Marriage" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Page" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Person" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Place" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Profession" TO kaira;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "siirtokarjalaisten_tie" TO kaira;