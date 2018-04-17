from playhouse.postgres_ext import *
from db_management.database_config import CONFIG
from db_management.katiha_models import KatihaPerson

database_proxy = Proxy()    # FIXME: This is likely not needed anymore since the connection is in shared module.


def set_database_to_models(database):
    database_proxy.initialize(database)
    database_proxy.register_fields({'point': 'POINT'})


class PointField(Field):
    db_field = 'point'


def pft(latitude, longitude):
    return fn.ST_SetSRID(fn.St_MakePoint(latitude, longitude), 4326)


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database_proxy
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


class KairaUpdateReportModel(Model):
    class Meta:
        database = database_proxy
        schema = 'system'
        db_table = 'KairaUpdateReport'

    time = DateTimeField()
    kairaFileName = TextField()
    changedRecordsCount = JSONField()
    recordCountChange = JSONField()
    ignoredRecordsCount = JSONField()
    comment = TextField(null=True)


class Place(BaseModel):
    latitude = TextField()
    longitude = TextField()
    name = TextField()
    stemmedName = TextField()
    extractedName = TextField()
    region = TextField()
    location = PointField()
    ambiguousRegion = BooleanField(default=False)
    markRowForRemoval = BooleanField(default=False)
    editLog = BinaryJSONField()

    class Meta:
        db_table = 'Place'


class Page(BaseModel):
    pageNumber = TextField(primary_key=True)

    class Meta:
        db_table = 'Page'


class Profession(BaseModel):
    name = TextField(unique=True)
    englishName = TextField(null=True)
    SESgroup1989 = IntegerField(null=True)
    socialClassRank = IntegerField(null=True)
    occupationCategory = IntegerField(null=True)
    agricultureOrForestryRelated = BooleanField(null=True)
    education = BooleanField(null=True)
    manualLabor = BooleanField(null=True)
    markRowForRemoval = BooleanField(default=False)

    def set_missing_properties(self, data_to_insert):
        """
        Check if some of the attributes are missing from the model to know if it should be
        updated.
        :param data_to_insert:
        :return:
        """
        change = False
        for key, value in data_to_insert.items():
            if getattr(self, key, None) is None and value is not None:
                if not change:
                    change = True
                setattr(self, key, value)

        return change

    class Meta:
        db_table = 'Profession'


class FarmDetails(BaseModel):
    animalHusbandry = BooleanField(default=False)
    dairyFarm = BooleanField(default=False)
    coldFarm = BooleanField(default=False)
    asutustila = BooleanField(default=False)
    maanhankintalaki = BooleanField(default=False)
    farmTotalArea = FloatField(default=None)
    editLog = BinaryJSONField()

    class Meta:
        db_table = 'FarmDetails'


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
    formerSurname = TextField()
    professionId = ForeignKeyField(db_column='professionId', null=True, rel_model=Profession, to_field='id')
    returnedKarelia = TextField()
    sex = TextField()
    servedDuringWar = BooleanField(null=True)
    injuredInWar = BooleanField(null=True)
    lotta = BooleanField(null=True)
    foodLotta = BooleanField(null=True)
    officeLotta = BooleanField(null=True)
    nurseLotta = BooleanField(null=True)
    antiairLotta = BooleanField(null=True)
    pikkulotta = BooleanField(null=True)
    organizationLotta = BooleanField(null=True)
    martta = BooleanField(null=True)
    katihaId = ForeignKeyField(db_column='katihaId', null=True, rel_model=KatihaPerson, to_field='id')
    farmDetailsId = ForeignKeyField(db_column='farmDetailsId', null=True, rel_model=FarmDetails, to_field='id')
    editLog = BinaryJSONField()
    markRowForRemoval = BooleanField(default=False)

    @staticmethod
    def create_or_get(data):
        try:
            with database_proxy.atomic():
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
    markRowForRemoval = BooleanField(default=False)

    @staticmethod
    def create_or_get(data):
        try:
            with database_proxy.atomic():
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
            with database_proxy.atomic():
                return LivingRecord.create(**data)
        except IntegrityError:
            # this is a unique column, so this row already exists,
            # making it safe to call .get().
            return LivingRecord.get(data)

    class Meta:
        db_table = 'LivingRecord'

class Marriage(BaseModel):
    primaryId = ForeignKeyField(db_column='primaryId', rel_model=Person,
                                to_field='id', related_name='marriage_Person_primaryId_set')
    spouseId = ForeignKeyField(db_column='spouseId', rel_model=Person,
                               to_field='id', related_name='marriage_Person_spouseId_set')
    weddingYear = IntegerField(null=True)
    editLog = BinaryJSONField()
    markRowForRemoval = BooleanField(default=False)

    class Meta:
        db_table = 'Marriage'

models = [BaseModel]
