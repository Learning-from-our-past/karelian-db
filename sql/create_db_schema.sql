--create database "learning-from-our-past"
create schema siirtokarjalaisten_tie;
create schema extensions;
CREATE EXTENSION postgis SCHEMA extensions;
ALTER DATABASE "learning-from-our-past" SET search_path=extensions, public;

CREATE TABLE siirtokarjalaisten_tie.Place(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  location extensions.GEOMETRY(POINT, 4326), -- WGS 84
  latitude TEXT NOT NULL,
  longitude TEXT NOT NULL,
  region TEXT NOT NULL,

  unique(name, region, latitude, longitude)
);


CREATE INDEX Place_gix
ON siirtokarjalaisten_tie.Place
USING GIST (location);

CREATE TABLE siirtokarjalaisten_tie.Page(
  pagenumber TEXT PRIMARY KEY NOT NULL   -- string with 5-6 like numbering
);

CREATE TABLE siirtokarjalaisten_tie.Profession(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  unique(name)
);

CREATE TABLE siirtokarjalaisten_tie.PersonDate(
  id SERIAL PRIMARY KEY,
  day INTEGER DEFAULT 0 CHECK(day >= 0 AND day <= 31),
  month INTEGER  DEFAULT 0 CHECK(month >= 0 AND month <= 12),
  year INTEGER DEFAULT 0 CHECK(year >= 0 AND year <= 2000),

  unique(day, month, year)
);

-- Required to make unique constraint to take in account NULL fields
CREATE UNIQUE INDEX Unique_index_PersonDate_day_month_year
  ON siirtokarjalaisten_tie.PersonDate
  (coalesce(day, 0), coalesce(month, 0), coalesce(year, 0));

CREATE TABLE siirtokarjalaisten_tie.Person(
  id SERIAL PRIMARY KEY,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  prevlastname TEXT,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  birthdate INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplace INTEGER REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathdate INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id) -- at the moment useless attrubte for Person since in the book main people don't have death data
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathplace INTEGER REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  ownhouse BOOLEAN,
  profession INTEGER REFERENCES siirtokarjalaisten_tie.Profession(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  returnedkarelia BOOLEAN,
  previousmarriages BOOLEAN,
  pagenumber TEXT NOT NULL REFERENCES siirtokarjalaisten_tie.Page(pagenumber)
      ON UPDATE CASCADE
      ON DELETE NO ACTION,
  origtext TEXT NOT NULL
);

CREATE TABLE siirtokarjalaisten_tie.Child(
  id SERIAL PRIMARY KEY,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  birthdate INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplace INTEGER REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  parent INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie.Person(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE
);

CREATE TABLE siirtokarjalaisten_tie.Spouse(
  id SERIAL PRIMARY KEY,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  prevlastname TEXT,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  birthdate INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplace INTEGER REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathdate INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  profession INTEGER REFERENCES siirtokarjalaisten_tie.Profession(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  spouse INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie.Person
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  marriageyear INTEGER
);

CREATE TABLE siirtokarjalaisten_tie.LivingRecord(
  id SERIAL PRIMARY KEY,
  person INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie.Person(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  place INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE NO ACTION,
  movedin INTEGER,
  movedout INTEGER
);
