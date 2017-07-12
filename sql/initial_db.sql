-- create database "learning-from-our-past";

create schema extensions;
CREATE EXTENSION postgis SCHEMA extensions;
CREATE EXTENSION plpython3u;
ALTER DATABASE "learning-from-our-past" SET search_path=extensions, public;
CREATE EXTENSION fuzzystrmatch SCHEMA extensions;