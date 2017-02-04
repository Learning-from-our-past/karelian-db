CREATE TABLE Place(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  location GEOMETRY(POINT, 4326), -- WGS 84
  latitude TEXT NOT NULL,
  longitude TEXT NOT NULL,
  region TEXT NOT NULL,

  unique(name, region, latitude, longitude)
);


CREATE INDEX Place_gix
ON Place
USING GIST (location);

CREATE TABLE Page(
  pagenumber TEXT PRIMARY KEY NOT NULL   -- string with 5-6 like numbering
);

CREATE TABLE Profession(
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  unique(name)
);

CREATE TABLE PersonDate(
  id SERIAL PRIMARY KEY,
  day INTEGER DEFAULT 0 CHECK(day >= 0 AND day <= 31),
  month INTEGER  DEFAULT 0 CHECK(month >= 0 AND month <= 12),
  year INTEGER DEFAULT 0 CHECK(year >= 0 AND year <= 2000),

  unique(day, month, year)
);

-- Required to make unique constraint to take in account NULL fields
CREATE UNIQUE INDEX Unique_index_PersonDate_day_month_year
  ON PersonDate
  (coalesce(day, 0), coalesce(month, 0), coalesce(year, 0));

CREATE TABLE Person(
  id SERIAL PRIMARY KEY,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  prevlastname TEXT,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  birthdate INTEGER REFERENCES PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplace INTEGER REFERENCES Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathdate INTEGER REFERENCES PersonDate(id) -- at the moment useless attrubte for Person since in the book main people don't have death data
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathplace INTEGER REFERENCES Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  ownhouse BOOLEAN,
  profession INTEGER REFERENCES Profession(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  returnedkarelia BOOLEAN,
  previousmarriages BOOLEAN,
  pagenumber TEXT NOT NULL REFERENCES Page(pagenumber)
      ON UPDATE CASCADE
      ON DELETE NO ACTION,
  origtext TEXT NOT NULL
);

CREATE TABLE Child(
  id SERIAL PRIMARY KEY,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  birthdate INTEGER REFERENCES PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplace INTEGER REFERENCES Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  parent INTEGER NOT NULL REFERENCES Person(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE
);

CREATE TABLE Spouse(
  id SERIAL PRIMARY KEY,
  firstname TEXT NOT NULL,
  lastname TEXT NOT NULL,
  prevlastname TEXT,
  sex TEXT NOT NULL CHECK(sex = 'm' OR sex = 'f' OR sex = ''),
  birthdate INTEGER REFERENCES PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  birthplace INTEGER REFERENCES Place(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  deathdate INTEGER REFERENCES PersonDate(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  profession INTEGER REFERENCES Profession(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,
  spouse INTEGER NOT NULL REFERENCES Person
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  marriageyear INTEGER
);

CREATE TABLE LivingRecord(
  id SERIAL PRIMARY KEY,
  person INTEGER NOT NULL REFERENCES Person(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,
  place INTEGER NOT NULL REFERENCES Place(id)
      ON UPDATE CASCADE
      ON DELETE NO ACTION,
  movedin INTEGER,
  movedout INTEGER
);

-- Enable PostGIS (includes raster)
CREATE EXTENSION postgis;
-- Enable Topology
CREATE EXTENSION postgis_topology;
-- Enable PostGIS Advanced 3D
-- and other geoprocessing algorithms
-- sfcgal not available with all distributions
CREATE EXTENSION postgis_sfcgal;
