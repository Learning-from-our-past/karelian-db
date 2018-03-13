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