from peewee import *
from models.db_connection import db_connection

database = db_connection.get_database()

class PointField(Field):
    db_field = 'point'

database.register_fields({'point': 'POINT'})

def pft(latitude, longitude):
    return fn.ST_SetSRID(fn.St_MakePoint(latitude, longitude), 4326)

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database
        schema = 'siirtokarjalaisten_tie'

class Place(BaseModel):
    latitude = TextField()
    longitude = TextField()
    name = TextField()
    region = TextField()
    location = PointField()

    class Meta:
        db_table = 'place'

class Persondate(BaseModel):
    day = IntegerField(null=True)
    month = IntegerField(null=True)
    year = IntegerField(null=True)

    class Meta:
        db_table = 'persondate'
        indexes = (
            (('day', 'month', 'year'), True),
        )

class Page(BaseModel):
    pagenumber = TextField(primary_key=True)

    class Meta:
        db_table = 'page'

class Profession(BaseModel):
    name = TextField(unique=True)

    class Meta:
        db_table = 'profession'

class Person(BaseModel):
    birthdate = ForeignKeyField(db_column='birthdate', null=True, rel_model=Persondate, to_field='id')
    birthplace = ForeignKeyField(db_column='birthplace', null=True, rel_model=Place, to_field='id')
    deathdate = ForeignKeyField(db_column='deathdate', null=True, rel_model=Persondate, related_name='persondate_deathdate_set', to_field='id')
    deathplace = ForeignKeyField(db_column='deathplace', null=True, rel_model=Place, related_name='place_deathplace_set', to_field='id')
    firstname = TextField()
    lastname = TextField()
    origtext = TextField()
    ownhouse = BooleanField(null=True)
    pagenumber = ForeignKeyField(db_column='pagenumber', rel_model=Page, to_field='pagenumber')
    previousmarriages = BooleanField(null=True)
    prevlastname = TextField(null=True)
    profession = ForeignKeyField(db_column='profession', null=True, rel_model=Profession, to_field='id')
    returnedkarelia = BooleanField(null=True)
    sex = TextField()

    class Meta:
        db_table = 'person'

class Child(BaseModel):
    birthdate = ForeignKeyField(db_column='birthdate', null=True, rel_model=Persondate, to_field='id')
    birthplace = ForeignKeyField(db_column='birthplace', null=True, rel_model=Place, to_field='id')
    firstname = TextField()
    lastname = TextField()
    parent = ForeignKeyField(db_column='parent', rel_model=Person, to_field='id')
    sex = TextField()

    class Meta:
        db_table = 'child'

class Livingrecord(BaseModel):
    movedin = IntegerField(null=True)
    movedout = IntegerField(null=True)
    person = ForeignKeyField(db_column='person', rel_model=Person, to_field='id')
    place = ForeignKeyField(db_column='place', rel_model=Place, to_field='id')

    class Meta:
        db_table = 'livingrecord'

class Spouse(BaseModel):
    birthdate = ForeignKeyField(db_column='birthdate', null=True, rel_model=Persondate, to_field='id')
    birthplace = ForeignKeyField(db_column='birthplace', null=True, rel_model=Place, to_field='id')
    deathdate = ForeignKeyField(db_column='deathdate', null=True, rel_model=Persondate, related_name='persondate_spouse_deathdate_set', to_field='id')
    firstname = TextField()
    lastname = TextField()
    marriageyear = IntegerField(null=True)
    prevlastname = TextField(null=True)
    profession = ForeignKeyField(db_column='profession', null=True, rel_model=Profession, to_field='id')
    sex = TextField()
    spouse = ForeignKeyField(db_column='spouse', rel_model=Person, to_field='id')

    class Meta:
        db_table = 'spouse'

