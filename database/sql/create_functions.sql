CREATE OR REPLACE FUNCTION truncate_tables(username IN VARCHAR, targetschema IN VARCHAR) RETURNS void AS $$
DECLARE
    statements CURSOR FOR
        SELECT tablename, schemaname FROM pg_tables
        WHERE tableowner = username AND schemaname = targetschema;
BEGIN
    FOR stmt IN statements LOOP
         EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.schemaname) || '.' || quote_ident(stmt.tablename) || ' CASCADE;';
    END LOOP;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION inttobool(integer, boolean) RETURNS boolean
AS $$
   SELECT CASE WHEN $1=0 and NOT $2 OR ($1<>0 and $2) THEN true ELSE false END  
$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION inttobool(boolean, integer) RETURNS boolean
AS $$
   SELECT inttobool($2, $1);
$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION notinttobool(boolean, integer) RETURNS boolean
AS 
$$
  SELECT NOT inttobool($2,$1);
$$
LANGUAGE sql;

CREATE OR REPLACE FUNCTION notinttobool(integer, boolean) RETURNS boolean
AS $$
	SELECT NOT inttobool($1,$2);
$$
LANGUAGE sql;

CREATE OPERATOR = (
PROCEDURE = inttobool,
LEFTARG = boolean,
RIGHTARG = integer,
COMMUTATOR = =,
NEGATOR = <>
);

CREATE OPERATOR <> (
PROCEDURE = notinttobool,
LEFTARG = integer,
RIGHTARG = boolean,
COMMUTATOR = <>,
NEGATOR = =
);

CREATE OPERATOR = (
PROCEDURE = inttobool,
LEFTARG = integer,
RIGHTARG = boolean,
COMMUTATOR = =,
NEGATOR = <>
);

CREATE OPERATOR <> (
PROCEDURE = notinttobool,
LEFTARG = boolean,
RIGHTARG = integer,
COMMUTATOR = <>,
NEGATOR = =
);