
-- Generated with https://wiki.postgresql.org/wiki/Fixing_Sequences
-- SELECT 'SELECT SETVAL(' ||
--        quote_literal(quote_ident(PGT.schemaname) || '.' || quote_ident(S.relname)) ||
--        ', COALESCE(MAX(' ||quote_ident(C.attname)|| '), 1) ) FROM ' ||
--        quote_ident(PGT.schemaname)|| '.'||quote_ident(T.relname)|| ';'
-- FROM pg_class AS S,
--      pg_depend AS D,
--      pg_class AS T,
--      pg_attribute AS C,
--      pg_tables AS PGT
-- WHERE S.relkind = 'S'
--     AND S.oid = D.objid
--     AND D.refobjid = T.oid
--     AND D.refobjid = C.attrelid
--     AND D.refobjsubid = C.attnum
--     AND T.relname = PGT.tablename
-- ORDER BY S.relname;


SELECT SETVAL('siirtokarjalaisten_tie."Child_id_seq"', COALESCE(MAX(id), 1) ) FROM siirtokarjalaisten_tie."Child";
SELECT SETVAL('siirtokarjalaisten_tie."LivingRecord_id_seq"', COALESCE(MAX(id), 1) ) FROM siirtokarjalaisten_tie."LivingRecord";
SELECT SETVAL('siirtokarjalaisten_tie."Marriage_id_seq"', COALESCE(MAX(id), 1) ) FROM siirtokarjalaisten_tie."Marriage";
SELECT SETVAL('siirtokarjalaisten_tie."Person_id_seq"', COALESCE(MAX(id), 1) ) FROM siirtokarjalaisten_tie."Person";
SELECT SETVAL('siirtokarjalaisten_tie."Place_id_seq"', COALESCE(MAX(id), 1) ) FROM siirtokarjalaisten_tie."Place";
SELECT SETVAL('siirtokarjalaisten_tie."Profession_id_seq"', COALESCE(MAX(id), 1) ) FROM siirtokarjalaisten_tie."Profession";
SELECT SETVAL('audit.logged_actions_event_id_seq', COALESCE(MAX(event_id), 1) ) FROM audit.logged_actions;
SELECT SETVAL('system.migratehistory_id_seq', COALESCE(MAX(id), 1) ) FROM system.migratehistory;
