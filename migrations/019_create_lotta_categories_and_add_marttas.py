"""Peewee migrations -- 020_migration_name.py.

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
    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "foodLotta" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."foodLotta" is 'Whether the source text contains mention of person having participated in food lotta activities. ("muonituslotta", "kanttiinilotta")';

    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "officeLotta" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."officeLotta" is 'Whether the source text contains mention of person having participated in office lotta activities. ("kanslialotta", "toimistolotta", "keskuslotta", "puhelinlotta", "viestilotta")';

    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "nurseLotta" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."nurseLotta" is 'Whether the source text contains mention of person having participated in nurse lotta activities. ("lääkintälotta")';
    
    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "antiairLotta" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."antiairLotta" is 'Whether the source text contains mention of person having participated in antiair lotta activities. ("iv-lotta", "ilmavalvontalotta")';
        
    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "pikkulotta" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."pikkulotta" is 'Whether the source text contains mention of person having participated in pikkulotta activities. ("pikkulotta")';
    
    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "organizationLotta" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."organizationLotta" is 'Whether the source text contains mention of person having participated in the lotta organization and there is nothing more specific about their participation. ("Lotta Svärd", "lottajärjestö", "lottayhdistys")';
    
    ALTER TABLE siirtokarjalaisten_tie."Person" ADD COLUMN "martta" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Person"."martta" is 'Whether the source text contains mention of person having participated in the martta organization. ("marttayhdistys", "marttajärjestö", "marttaseura", "marttatoiminta", "marttaliitto", "marttakerho", "marttoihin", "marttojen")';
    """)


def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

