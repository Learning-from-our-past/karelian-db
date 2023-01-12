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


class BirthInMarriageCode(BaseModel):
    code = PrimaryKeyField(db_column='code')
    birthType = TextField()

    class Meta:
        db_table = 'BirthInMarriageCode'


class DepartureType(BaseModel):
    type = TextField()

    class Meta:
        db_table = 'DepartureType'


class KatihaPerson(BaseModel):
    familyId = ForeignKeyField(db_column='familyId', null=True, model=Family, to_field='id')
    motherLanguageId = ForeignKeyField(db_column='motherLanguageId', null=True, model=Language, to_field='id')
    birthDay = IntegerField()
    birthMonth = IntegerField()
    birthYear = IntegerField()
    sex = TextField()
    birthInMarriage = ForeignKeyField(db_column='birthInMarriage', null=True, model=BirthInMarriageCode, to_field='code')
    multipleBirth = IntegerField()
    vaccinated = BooleanField()
    rokko = BooleanField()
    literate = BooleanField()
    literacyConfirmed = BooleanField()
    departureTypeId = ForeignKeyField(db_column='departureTypeId', null=True, model=DepartureType, to_field='id')
    departureDay = IntegerField()
    departureMonth = IntegerField()
    departureYear = IntegerField()

    class Meta:
        db_table = 'KatihaPerson'
