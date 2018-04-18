"""Peewee migrations -- 024_make_child_use_primary_parent_and_spouse_parent.py.

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
    ALTER TABLE siirtokarjalaisten_tie."Child" ADD COLUMN "primaryParentId"
      INTEGER REFERENCES siirtokarjalaisten_tie."Person"(id);
    ALTER TABLE siirtokarjalaisten_tie."Child" ADD COLUMN "spouseParentId"
      INTEGER REFERENCES siirtokarjalaisten_tie."Person"(id);
      
    -- First set primaryParentId for cases where we know one parent (one parent has to be primary)
    UPDATE siirtokarjalaisten_tie."Child"
      SET "primaryParentId" = CASE WHEN "fatherId" IS NULL 
        THEN "motherId" END
        WHERE "primaryParentId" IS NULL;
      
    UPDATE siirtokarjalaisten_tie."Child"
      SET "primaryParentId" = CASE WHEN "motherId" IS NULL
        THEN "fatherId" END
        WHERE "primaryParentId" IS NULL;
    
    -- Then set both primaryParentId and spouseParentId for cases where both parents are known
    UPDATE siirtokarjalaisten_tie."Child"
      SET "primaryParentId" = CASE WHEN 
        "fatherId" IS NOT NULL AND p."primaryPerson" IS TRUE
        THEN "fatherId" ELSE "motherId" END
      FROM "siirtokarjalaisten_tie"."Person" p
      WHERE p.id = "fatherId" AND "primaryParentId" IS NULL;
        
    UPDATE siirtokarjalaisten_tie."Child"
      SET "spouseParentId" = m."spouseId" FROM siirtokarjalaisten_tie."Marriage" m
        WHERE m."primaryId" = "primaryParentId";
    
    DROP INDEX IF EXISTS siirtokarjalaisten_tie.child_fatherid_index;
    DROP INDEX IF EXISTS siirtokarjalaisten_tie.child_motherid_index;
    
    ALTER TABLE siirtokarjalaisten_tie."Child" DROP COLUMN IF EXISTS "fatherId";
    ALTER TABLE siirtokarjalaisten_tie."Child" DROP COLUMN IF EXISTS "motherId";
    
    CREATE INDEX Child_primaryParentid_index ON siirtokarjalaisten_tie."Child" ("primaryParentId");
    CREATE INDEX Child_spouseParentId_index ON siirtokarjalaisten_tie."Child" ("spouseParentId");
    
    ALTER TABLE siirtokarjalaisten_tie."Child" ALTER COLUMN "primaryParentId" SET NOT NULL;
    """)


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""
