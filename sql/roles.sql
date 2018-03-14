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

do
$body$
declare
  num_users integer;
begin
   SELECT count(*)
     into num_users
   FROM pg_roles
   WHERE rolname = 'researcher';

   IF num_users = 0 THEN
      CREATE USER researcher;
   END IF;
end
$body$;

GRANT USAGE ON SCHEMA "siirtokarjalaisten_tie" TO researcher;
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Child" TO researcher;
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."LivingRecord" TO researcher;
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Marriage" TO researcher;
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Page" TO researcher;
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Person" TO researcher;
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Place" TO researcher;
GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "siirtokarjalaisten_tie"."Profession" TO researcher;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "siirtokarjalaisten_tie" TO researcher;

-- Views
GRANT SELECT ON "siirtokarjalaisten_tie"."MarriedPerson" TO researcher;


-- Create users
CREATE USER robert INHERIT;
CREATE USER john INHERIT;

GRANT researcher TO robert;
GRANT researcher TO john;
