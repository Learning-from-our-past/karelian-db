from playhouse.postgres_ext import *
from db_management.models.db_connection import db_connection
from config import CONFIG

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

    def get_editable_fields(self):
        edit_log = self.editLog

        if edit_log is None or bool(edit_log) is False:
            return None

        return {key: value for (key, value) in edit_log.items() if value['author'] in CONFIG['users_whose_edits_can_be_overridden']}

    def get_non_editable_fields(self):
        edit_log = self.editLog

        if edit_log is None or bool(edit_log) is False:
            return None

        return {key: value for (key, value) in edit_log.items() if
                value['author'] not in CONFIG['users_whose_edits_can_be_overridden']}


class Place(BaseModel):
    latitude = TextField()
    longitude = TextField()
    name = TextField()
    stemmedName = TextField()
    extractedName = TextField()
    region = TextField()
    location = PointField()
    ambiguousRegion = BooleanField(default=False)
    editLog = BinaryJSONField()

    class Meta:
        db_table = 'Place'


class Page(BaseModel):
    pageNumber = TextField(primary_key=True)

    class Meta:
        db_table = 'Page'

class Profession(BaseModel):
    name = TextField(unique=True)

    class Meta:
        db_table = 'Profession'

class Person(BaseModel):
    kairaId = TextField()
    birthDay = IntegerField()
    birthMonth = IntegerField()
    birthYear = IntegerField()
    birthPlaceId = ForeignKeyField(db_column='birthPlaceId', null=True, rel_model=Place, to_field='id')
    deathDay = IntegerField()
    primaryPerson = BooleanField()
    deathMonth = IntegerField()
    deathYear = IntegerField()
    deathPlaceId = ForeignKeyField(db_column='deathPlaceId', null=True, rel_model=Place, related_name='Place_deathPlace_set', to_field='id')
    firstName = TextField()
    lastName = TextField()
    originalText = TextField()
    sourceTextId = TextField()
    ownHouse = BooleanField(null=True)
    pageNumber = ForeignKeyField(db_column='pageNumber', rel_model=Page, to_field='pageNumber')
    previousMarriages = TextField(null=True)
    prevLastName = TextField()
    professionId = ForeignKeyField(db_column='professionId', null=True, rel_model=Profession, to_field='id')
    returnedKarelia = TextField()
    sex = TextField()
    editLog = BinaryJSONField()

    @staticmethod
    def create_or_get(data):
        try:
            with database.atomic():
                return Person.create(**data)
        except IntegrityError:
            # this is a unique column, so this row already exists,
            # making it safe to call .get().
            return Person.get(data)

    class Meta:
        db_table = 'Person'

class Child(BaseModel):
    kairaId = TextField()
    birthYear = IntegerField()
    birthPlaceId = ForeignKeyField(db_column='birthPlaceId', null=True, rel_model=Place, to_field='id')
    firstName = TextField()
    lastName = TextField()
    fatherId = ForeignKeyField(db_column='fatherId', null=True, rel_model=Person, to_field='id', related_name='child_Person_fatherId_set')
    motherId = ForeignKeyField(db_column='motherId', null=True, rel_model=Person, to_field='id', related_name='child_Person_motherId_set')
    sex = TextField()
    sourceTextId = TextField()
    editLog = BinaryJSONField()

    @staticmethod
    def create_or_get(data):
        try:
            with database.atomic():
                return Child.create(**data)
        except IntegrityError:
            # this is a unique column, so this row already exists,
            # making it safe to call .get().
            return Child.get(data)

    class Meta:
        db_table = 'Child'

class LivingRecord(BaseModel):
    movedIn = IntegerField(null=True)
    movedOut = IntegerField(null=True)
    personId = ForeignKeyField(db_column='personId', rel_model=Person, to_field='id')
    placeId = ForeignKeyField(db_column='placeId', rel_model=Place, to_field='id')
    editLog = BinaryJSONField()

    @staticmethod
    def create_or_get(data):
        try:
            with database.atomic():
                return LivingRecord.create(**data)
        except IntegrityError:
            # this is a unique column, so this row already exists,
            # making it safe to call .get().
            return LivingRecord.get(data)

    class Meta:
        db_table = 'LivingRecord'

class Marriage(BaseModel):
    manId = ForeignKeyField(db_column='manId', rel_model=Person, to_field='id', related_name='marriage_Person_manId_set')
    womanId = ForeignKeyField(db_column='womanId', rel_model=Person, to_field='id', related_name='marriage_Person_womanId_set')
    weddingYear = IntegerField(null=True)
    editLog = BinaryJSONField()

    class Meta:
        db_table = 'Marriage'
