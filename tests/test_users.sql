DO
$body$
BEGIN
   IF NOT EXISTS (
      SELECT
      FROM   pg_catalog.pg_user
      WHERE  usename = 'john') THEN
      CREATE USER john;
   END IF;
END
$body$;

ALTER USER john WITH PASSWORD '1234';
GRANT "researcher" TO john;