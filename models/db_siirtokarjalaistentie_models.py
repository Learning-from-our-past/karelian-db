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
        db_table = 'Place'

class PersonDate(BaseModel):
    day = IntegerField(null=True)
    month = IntegerField(null=True)
    year = IntegerField(null=True)

    class Meta:
        db_table = 'PersonDate'
        indexes = (
            (('day', 'month', 'year'), True),
        )

class Page(BaseModel):
    pageNumber = TextField(primary_key=True)

    class Meta:
        db_table = 'Page'

class Profession(BaseModel):
    name = TextField(unique=True)

    class Meta:
        db_table = 'Profession'

class Person(BaseModel):
    birthDateId = ForeignKeyField(db_column='birthDateId', null=True, rel_model=PersonDate, to_field='id')
    birthPlaceId = ForeignKeyField(db_column='birthPlaceId', null=True, rel_model=Place, to_field='id')
    deathDateId = ForeignKeyField(db_column='deathDateId', null=True, rel_model=PersonDate, related_name='PersonDate_deathDate_set', to_field='id')
    deathPlaceId = ForeignKeyField(db_column='deathPlaceId', null=True, rel_model=Place, related_name='Place_deathPlace_set', to_field='id')
    firstName = TextField()
    lastName = TextField()
    originalText = TextField()
    ownHouse = BooleanField(null=True)
    pageNumber = ForeignKeyField(db_column='pageNumber', rel_model=Page, to_field='pageNumber')
    previousMarriages = BooleanField(null=True)
    prevLastName = TextField(null=True)
    professionId = ForeignKeyField(db_column='professionId', null=True, rel_model=Profession, to_field='id')
    returnedKarelia = BooleanField(null=True)
    sex = TextField()

    class Meta:
        db_table = 'Person'

class Child(BaseModel):
    birthDateId = ForeignKeyField(db_column='birthDateId', null=True, rel_model=PersonDate, to_field='id')
    birthPlaceId = ForeignKeyField(db_column='birthPlaceId', null=True, rel_model=Place, to_field='id')
    firstName = TextField()
    lastName = TextField()
    fatherId = ForeignKeyField(db_column='fatherId', null=True, rel_model=Person, to_field='id', related_name='child_Person_fatherId_set')
    motherId = ForeignKeyField(db_column='motherId', null=True, rel_model=Person, to_field='id', related_name='child_Person_motherId_set')
    sex = TextField()

    class Meta:
        db_table = 'Child'

class Livingrecord(BaseModel):
    movedIn = IntegerField(null=True)
    movedOut = IntegerField(null=True)
    personId = ForeignKeyField(db_column='personId', rel_model=Person, to_field='id')
    placeId = ForeignKeyField(db_column='placeId', rel_model=Place, to_field='id')

    class Meta:
        db_table = 'LivingRecord'

class Marriage(BaseModel):
    manId = ForeignKeyField(db_column='manId', rel_model=Person, to_field='id', related_name='marriage_Person_manId_set')
    womanId = ForeignKeyField(db_column='womanId', rel_model=Person, to_field='id', related_name='marriage_Person_womanId_set')
    weddingYear = IntegerField(null=True)

    class Meta:
        db_table = 'Marriage'
