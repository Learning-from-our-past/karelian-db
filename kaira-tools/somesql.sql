-- some sql for posteriority for now

create table kairatools."Role" (
  "id" SERIAL,
  "name" VARCHAR,
  "description" TEXT
);

CREATE UNIQUE INDEX "Role_name_uindex" ON kairatools."Role" (name);

CREATE TABLE kairatools."User"(
  id SERIAL PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  name TEXT,
  role TEXT DEFAULT 'user',
  picture TEXT,
  active BOOLEAN DEFAULT FALSE,
  confirmed_at TIMESTAMP
);

create table kairatools."UserRoles" (
  id SERIAL PRIMARY KEY,
  "user_id" INTEGER REFERENCES kairatools."User"(id),
  "role_id" INTEGER REFERENCES kairatools."Role"(id)
);