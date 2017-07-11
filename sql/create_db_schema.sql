--create database "learning-from-our-past"
create schema siirtokarjalaisten_tie;
create schema extensions;
CREATE EXTENSION postgis SCHEMA extensions;
CREATE EXTENSION plpython3u;
ALTER DATABASE "learning-from-our-past" SET search_path=extensions, public;

CREATE EXTENSION fuzzystrmatch SCHEMA extensions;

CREATE TABLE siirtokarjalaisten_tie."Place"(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  region TEXT,
  "stemmedName" TEXT,
  "extractedName" TEXT,
  location extensions.GEOMETRY(POINT, 4326), -- WGS 84
  latitude TEXT,
  longitude TEXT,
  "ambiguousRegion" BOOLEAN DEFAULT FALSE,
  unique(name, region, "stemmedName", "extractedName", latitude, longitude)
);


CREATE INDEX Place_gix
ON siirtokarjalaisten_tie."Place"
USING GIST (location);

CREATE TABLE siirtokarjalaisten_tie."Page"(
  "pageNumber" TEXT PRIMARY KEY NOT NULL   -- string with 5-6 like numbering
);

CREATE TABLE siirtokarjalaisten_tie."Profession"(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  unique(name)
);

CREATE TABLE siirtokarjalaisten_tie."Person"(
  id SERIAL PRIMARY KEY,
  "firstName" TEXT NOT NULL,
  "lastName" TEXT NOT NULL,
  "prevLastName" TEXT,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  "primaryPerson" BOOLEAN NOT NULL,
  "birthDay" INTEGER,
  "birthMonth" INTEGER,
  "birthYear" INTEGER,
  "birthPlaceId" INTEGER REFERENCES siirtokarjalaisten_tie."Place"(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  "deathDay" INTEGER,
  "deathMonth" INTEGER,
  "deathYear" INTEGER,
  "deathPlaceId" INTEGER REFERENCES siirtokarjalaisten_tie."Place"(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  "ownHouse" BOOLEAN,
  "professionId" INTEGER REFERENCES siirtokarjalaisten_tie."Profession"(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  "returnedKarelia" TEXT NOT NULL , -- MS Access can't make difference between NULL and False values of boolean field so we have to use TEXT...
  "previousMarriages" TEXT NOT NULL, -- MS Access can't make difference between NULL and False values of boolean field so we have to use TEXT...
  "pageNumber" TEXT NOT NULL REFERENCES siirtokarjalaisten_tie."Page"("pageNumber")
      ON UPDATE CASCADE
      ON DELETE NO ACTION,
  "originalText" TEXT NOT NULL,
  "editLog" JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE siirtokarjalaisten_tie."Child"(
  id SERIAL PRIMARY KEY,
  "firstName" TEXT NOT NULL,
  "lastName" TEXT NOT NULL,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  "birthYear" INTEGER,
  "birthPlaceId" INTEGER REFERENCES siirtokarjalaisten_tie."Place"(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  "fatherId" INTEGER REFERENCES siirtokarjalaisten_tie."Person"(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  "motherId" INTEGER REFERENCES siirtokarjalaisten_tie."Person"(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE
);

CREATE TABLE siirtokarjalaisten_tie."Marriage"(
  id SERIAL PRIMARY KEY,
  "manId" INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie."Person"(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  "womanId" INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie."Person"(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  "weddingYear" INTEGER
);

CREATE TABLE siirtokarjalaisten_tie."LivingRecord"(
  id SERIAL PRIMARY KEY,
  "personId" INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie."Person"(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  "placeId" INTEGER NOT NULL REFERENCES siirtokarjalaisten_tie."Place"(id)
      ON UPDATE CASCADE
      ON DELETE NO ACTION,
  "movedIn" INTEGER,
  "movedOut" INTEGER
);
