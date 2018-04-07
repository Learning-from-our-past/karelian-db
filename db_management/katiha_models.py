from peewee import *


database_proxy = Proxy()


def set_database_to_models(database):
    database_proxy.initialize(database)


class BaseModel(Model):
    class Meta:
        database = database_proxy
        schema = 'katiha'


class Language(BaseModel):
    language = TextField()

    class Meta:
        db_table = 'Language'


class Family(BaseModel):
    class Meta:
        db_table = 'Family'


class KatihaPerson(BaseModel):
    familyId = ForeignKeyField(db_column='familyId', null=True, rel_model=Family, to_field='id')
    motherLanguageId = ForeignKeyField(db_column='motherLanguageId', null=True, rel_model=Language, to_field='id')
    birthDay = IntegerField()
    birthMonth = IntegerField()
    birthYear = IntegerField()

    class Meta:
        db_table = 'KatihaPerson'
