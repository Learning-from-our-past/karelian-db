CREATE USER kaira;
GRANT USAGE ON SCHEMA "siirtokarjalaisten_tie" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Child" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."LivingRecord" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Marriage" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Page" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Person" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Place" TO kaira;
GRANT SELECT, INSERT, UPDATE, REFERENCES ON "siirtokarjalaisten_tie"."Profession" TO kaira;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "siirtokarjalaisten_tie" TO kaira;