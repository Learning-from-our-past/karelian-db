--create database "learning-from-our-past"
create schema siirtokarjalaisten_tie;
create schema extensions;
CREATE EXTENSION postgis SCHEMA extensions;
ALTER DATABASE "learning-from-our-past" SET search_path=extensions, public;

CREATE EXTENSION fuzzystrmatch SCHEMA extensions;

CREATE TABLE siirtokarjalaisten_tie.Place(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  location extensions.GEOMETRY(POINT, 4326), -- WGS 84
  latitude TEXT,
  longitude TEXT,
  region TEXT,

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
  birthdateId INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplaceId INTEGER REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathdateId INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id) -- at the moment useless attrubte for Person since in the book main people don't have death data
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathplaceId INTEGER REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  ownhouse BOOLEAN,
  professionId INTEGER REFERENCES siirtokarjalaisten_tie.Profession(id)
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
  birthdateId INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplaceId INTEGER REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  parentPersonId INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie.Person(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE
);

CREATE TABLE siirtokarjalaisten_tie.Spouse(
  id SERIAL PRIMARY KEY,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  maidenname TEXT,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  birthdateId INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplaceId INTEGER REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathdateId INTEGER REFERENCES siirtokarjalaisten_tie.PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  professionId INTEGER REFERENCES siirtokarjalaisten_tie.Profession(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  personId INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie.Person
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  marriageyear INTEGER
);

CREATE TABLE siirtokarjalaisten_tie.LivingRecord(
  id SERIAL PRIMARY KEY,
  personId INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie.Person(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  placeId INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie.Place(id)
      ON UPDATE CASCADE
      ON DELETE NO ACTION,
  movedin INTEGER,
  movedout INTEGER
);
