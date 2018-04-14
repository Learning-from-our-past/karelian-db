DO
$body$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_catalog.pg_user
      WHERE  usename = 'kaira') THEN
      CREATE USER kaira;
   END IF;
END
$body$;

ALTER DEFAULT PRIVILEGES
IN SCHEMA public
GRANT SELECT, INSERT ON tables TO kaira;

ALTER DEFAULT PRIVILEGES
IN SCHEMA public
GRANT SELECT, UPDATE ON sequences TO kaira;
