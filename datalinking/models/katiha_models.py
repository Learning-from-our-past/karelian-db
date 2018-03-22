from peewee import *


database_proxy = Proxy()


def set_database_to_models(database):
    database_proxy.initialize(database)


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database_proxy


class Codes(BaseModel):
    code = CharField()
    definition = TextField(null=True)
    type = CharField(null=True)

    class Meta:
        db_table = 'codes'


class Parishes(BaseModel):
    parishId = CharField(db_column='parishId', index=True, unique=True)
    parishName = CharField(db_column='parishName', null=True)

    class Meta:
        db_table = 'parishes'


class La(BaseModel):
    id = PrimaryKeyField(db_column='ID')
    arrivalDate = DateField(db_column='arrivalDate', null=True)
    arrivalDay = IntegerField(db_column='arrivalDay', null=True)
    arrivalMonth = IntegerField(db_column='arrivalMonth', null=True)
    arrivalType = CharField(db_column='arrivalType', null=True)
    arrivalYear = IntegerField(db_column='arrivalYear', null=True)
    birthDate = DateField(db_column='birthDate', null=True)
    birthDay = IntegerField(db_column='birthDay', null=True)
    birthInMarriage = CharField(db_column='birthInMarriage', null=True)
    birthMonth = IntegerField(db_column='birthMonth', null=True)
    birthParish = CharField(db_column='birthParish', null=True)
    birthYear = IntegerField(db_column='birthYear', null=True)
    confirmationDate = DateField(db_column='confirmationDate', null=True)
    confirmationDay = IntegerField(db_column='confirmationDay', null=True)
    confirmationMonth = IntegerField(db_column='confirmationMonth', null=True)
    confirmationYear = IntegerField(db_column='confirmationYear', null=True)
    confirmed = CharField(null=True)
    departureDate = DateField(db_column='departureDate', null=True)
    departureDay = IntegerField(db_column='departureDay', null=True)
    departureMonth = IntegerField(db_column='departureMonth', null=True)
    departureType = CharField(db_column='departureType', null=True)
    departureYear = IntegerField(db_column='departureYear', null=True)
    education = CharField(null=True)
    eventId = TextField(db_column='eventId', null=True)
    firstName = CharField(db_column='firstName', null=True)
    lastName = CharField(db_column='lastName', null=True)
    lastParish = CharField(db_column='lastParish', null=True)
    literate = CharField(null=True)
    motherLanguage = CharField(db_column='motherLanguage', null=True)
    multipleBirth = CharField(db_column='multipleBirth', null=True)
    occupation = CharField(null=True)
    parishId = CharField(db_column='parishId', null=True)
    patronymic = CharField(null=True)
    secondName = CharField(db_column='secondName', null=True)
    sex = CharField(null=True)
    vaccination = CharField(null=True)

    class Meta:
        db_table = 'LA'
        indexes = (
            (('keyId', 'eventId'), False),
        )
