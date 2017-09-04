"""Peewee migrations -- 014_migration_name.py.

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
    ALTER TABLE siirtokarjalaisten_tie."Profession" ADD COLUMN "englishName" TEXT DEFAULT NULL;
    ALTER TABLE siirtokarjalaisten_tie."Profession" ADD COLUMN "SESgroup1989" INTEGER DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Profession"."SESgroup1989" is 'Classification of SES groups statistics Finland 1989 (1=self-employed and employer farmers, 2=self-employed or empoyers, 3= upper level employees with administrative, managerial, professional and related occupations, 4= lower level employees with administrative and clerical occupations, 5= manual workers, 6=students, 7= pensioners, 8=others( e.g. unemployed or unknown)';
    ALTER TABLE siirtokarjalaisten_tie."Profession" ADD COLUMN "socialClassRank" INTEGER DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Profession"."socialClassRank" is 'New social class ranking (1940-1970 Finland) 1-high, 7-low';
    ALTER TABLE siirtokarjalaisten_tie."Profession" ADD COLUMN "occupationCategory" INTEGER DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Profession"."occupationCategory" is 'Categories from census RL recode (0=technical professionals, teachers, free professions; 1=directors, office workers typers etc. others; 2=business, selling; 3=agriculture and forestry related; 4=mining, industry; 5=transportation, 6=factory and craftsmen; 7=handicraft workers; 8=service)';
    
    ALTER TABLE siirtokarjalaisten_tie."Profession" ADD COLUMN "agricultureOrForestryRelated" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Profession"."agricultureOrForestryRelated" is 'Is profession related to agriculture or forestry. True, False or NULL (unknown)';
    ALTER TABLE siirtokarjalaisten_tie."Profession" ADD COLUMN "education" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Profession"."education" is 'Does profession involve education. True, False or NULL (unknown)';
    ALTER TABLE siirtokarjalaisten_tie."Profession" ADD COLUMN "manualLabor" BOOLEAN DEFAULT NULL;
    COMMENT ON COLUMN siirtokarjalaisten_tie."Profession"."manualLabor" is 'Does profession involve manual labor. True, False or NULL (unknown)'
    """)



def rollback(migrator, database, fake=False, **kwargs):
    """Write your rollback migrations here."""

