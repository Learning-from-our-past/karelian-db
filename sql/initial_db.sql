-- create database "learning-from-our-past";

CREATE SCHEMA IF NOT EXISTS extensions;
DROP SCHEMA IF EXISTS system CASCADE;
CREATE SCHEMA system;
CREATE EXTENSION IF NOT EXISTS postgis SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS plpython3u;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch SCHEMA extensions;

DROP SCHEMA IF EXISTS siirtokarjalaisten_tie CASCADE;
CREATE SCHEMA siirtokarjalaisten_tie;

-- ALTER DATABASE "karelian_testdb" SET search_path TO pg_catalog, siirtokarjalaisten_tie, public, extensions;
DO $$
BEGIN
    EXECUTE 'ALTER DATABASE ' || quote_ident(current_database()) || ' SET search_path TO pg_catalog, siirtokarjalaisten_tie, public, extensions';
END$$;
