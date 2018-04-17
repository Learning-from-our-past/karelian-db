"""Peewee migrations -- 021_add_more_katiha_columns.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['model_name']            # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.python(func, *args, **kwargs)        # Run python code
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.drop_index(model, *col_names)
    > migrator.add_not_null(model, *field_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)

"""

import datetime as dt
import peewee as pw


def migrate(migrator, database, fake=False, **kwargs):
    migrator.sql("""
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "sex" TEXT NULL;
    COMMENT ON COLUMN katiha."KatihaPerson".sex is 'Sex of person. f for female, m for male.';
    
    CREATE TABLE katiha."BirthInMarriageCode"(
      code SERIAL PRIMARY KEY,
      "birthType" TEXT NOT NULL
    );
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "birthInMarriage" INTEGER NULL REFERENCES katiha."BirthInMarriageCode"
      ON DELETE SET NULL
      ON UPDATE CASCADE;
    COMMENT ON COLUMN katiha."KatihaPerson"."birthInMarriage" is 'Whether the person was born in a marriage or not.';
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "multipleBirth" INTEGER NULL;
    COMMENT ON COLUMN katiha."KatihaPerson"."multipleBirth" is 'How many children were born when this person was born (i.e. twins) including this person.';
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "vaccinated" BOOLEAN NULL;
    COMMENT ON COLUMN katiha."KatihaPerson"."vaccinated" is 'Whether this person was vaccinated.';
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "rokko" BOOLEAN NULL;
    COMMENT ON COLUMN katiha."KatihaPerson"."rokko" is 'Whether this person suffered through a rokko disease, probably smallpox.';
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "literate" BOOLEAN NULL;
    COMMENT ON COLUMN katiha."KatihaPerson"."literate" is 'Whether this person self-reported as literate.';
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "literacyConfirmed" BOOLEAN NULL
      CHECK(
        ("literacyConfirmed" IS NOT NULL AND "literate" IS TRUE) OR
        ("literacyConfirmed" IS NULL)
      );
    COMMENT ON COLUMN katiha."KatihaPerson"."literacyConfirmed" is 'Whether the literacy of this person was confirmed.';
    
    CREATE TABLE katiha."DepartureType"(
      id SERIAL PRIMARY KEY,
      type TEXT NOT NULL
    );

    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "departureTypeId" INTEGER NULL REFERENCES katiha."DepartureType"
      ON DELETE SET NULL
      ON UPDATE CASCADE;
    COMMENT ON COLUMN katiha."KatihaPerson"."departureTypeId" is 'How the person departed the church book.';
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "departureDay" INTEGER NULL
      CHECK(
        ("departureDay" IS NOT NULL AND "departureTypeId" IS NOT NULL) OR
        ("departureDay" IS NULL)
      );
    COMMENT ON COLUMN katiha."KatihaPerson"."departureDay" is 'The day of departure.';
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "departureMonth" INTEGER NULL
      CHECK(
        ("departureMonth" IS NOT NULL AND "departureTypeId" IS NOT NULL) OR
        ("departureMonth" IS NULL)
      );
    COMMENT ON COLUMN katiha."KatihaPerson"."departureMonth" is 'The month of departure.';
    
    ALTER TABLE katiha."KatihaPerson" ADD COLUMN "departureYear" INTEGER NULL
      CHECK(
        ("departureYear" IS NOT NULL AND "departureTypeId" IS NOT NULL) OR
        ("departureYear" IS NULL)
      );;
    COMMENT ON COLUMN katiha."KatihaPerson"."departureYear" is 'The year of departure.';
    
    GRANT SELECT, INSERT, UPDATE, DELETE, REFERENCES ON "katiha"."DepartureType", "katiha"."BirthInMarriageCode" TO kaira;
    GRANT SELECT, REFERENCES ON "katiha"."DepartureType", "katiha"."BirthInMarriageCode" TO researcher;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA "katiha" TO researcher, kaira;
    """)


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""
