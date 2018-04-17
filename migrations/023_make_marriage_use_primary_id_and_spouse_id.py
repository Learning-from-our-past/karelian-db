"""Peewee migrations -- 023_migration_name.py.

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
    ALTER TABLE siirtokarjalaisten_tie."Marriage" ADD COLUMN "primaryId"
      INTEGER REFERENCES siirtokarjalaisten_tie."Person"(id);
    ALTER TABLE siirtokarjalaisten_tie."Marriage" ADD COLUMN "spouseId"
      INTEGER REFERENCES siirtokarjalaisten_tie."Person"(id);
      
    UPDATE siirtokarjalaisten_tie."Marriage"
      SET "primaryId" = CASE WHEN p."primaryPerson" IS TRUE THEN "manId" ELSE "womanId" END
      FROM "siirtokarjalaisten_tie"."Person" p
      WHERE p.id = "manId";
         
    UPDATE siirtokarjalaisten_tie."Marriage"
      SET "spouseId" = CASE WHEN p."primaryPerson" IS FALSE THEN "manId" ELSE "womanId" END
      FROM "siirtokarjalaisten_tie"."Person" p
      WHERE p.id = "manId";
         
    ALTER TABLE siirtokarjalaisten_tie."Marriage" ALTER COLUMN "primaryId" SET NOT NULL;
    ALTER TABLE siirtokarjalaisten_tie."Marriage" ALTER COLUMN "spouseId" SET NOT NULL;
    
    DROP VIEW IF EXISTS "siirtokarjalaisten_tie"."MarriedPerson";
    
    DROP INDEX IF EXISTS siirtokarjalaisten_tie.marriage_manid_index;
    DROP INDEX IF EXISTS siirtokarjalaisten_tie.marriage_womanid_index;
    
    ALTER TABLE siirtokarjalaisten_tie."Marriage" DROP COLUMN IF EXISTS "manId";
    ALTER TABLE siirtokarjalaisten_tie."Marriage" DROP COLUMN IF EXISTS "womanId";
    
    CREATE INDEX Marriage_primaryId_index ON siirtokarjalaisten_tie."Marriage" ("primaryId");
    CREATE INDEX Marriage_spouseId_index ON siirtokarjalaisten_tie."Marriage" ("spouseId");
    
    CREATE VIEW siirtokarjalaisten_tie."MarriedPerson" AS
          SELECT *
          FROM "siirtokarjalaisten_tie"."Person"
          WHERE "previousMarriages" = 'true'
          OR ("formerSurname" IS NOT NULL AND sex = 'f')
          OR EXISTS(SELECT 1
                FROM "siirtokarjalaisten_tie"."Marriage"
                WHERE "Marriage"."primaryId" = "Person".id OR "Marriage"."spouseId" = "Person".id);
    """)


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""
