from peewee import *


database_proxy = Proxy()


def set_database_to_models(database):
    database_proxy.initialize(database)


class BaseModel(Model):
    class Meta:
        database = database_proxy
        schema = 'divaevi'


class DivaeviPerson(BaseModel):
    birthDay = IntegerField()
    birthMonth = IntegerField()
    birthYear = IntegerField()

    class Meta:
        db_table = 'DivaeviPerson'
