from playhouse.postgres_ext import *
from models.db_connection import db_connection
from flask_security import RoleMixin, UserMixin


class KairaToolsBaseModel(Model):
    class Meta:
        database = db_connection.get_database()
        schema = 'kairatools'


class Role(KairaToolsBaseModel, RoleMixin):
    name = CharField(unique=True)
    description = TextField(null=True)

    default_roles = {
        'super': 'superuser',
        'researcher': 'researcher'
    }

    class Meta:
        db_table = 'Role'


class User(KairaToolsBaseModel, UserMixin):
    email = TextField()
    password = TextField()
    name = TextField(null=True)
    picture = TextField(null=True)
    active = BooleanField()
    confirmed_at = DateTimeField(null=True)
    last_login_at = DateTimeField(null=True)
    current_login_at = DateTimeField(null=True)
    last_login_ip = TextField(null=True)
    current_login_ip = TextField(null=True)
    login_count = IntegerField(default=0)

    class Meta:
        db_table = 'User'


class UserRole(KairaToolsBaseModel):
    # Because peewee does not come with built-in many-to-many
    # relationships, we need this intermediary class to link
    # user to roles.
    user = ForeignKeyField(User, related_name='roles')
    role = ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)

    class Meta:
        db_table = 'UserRole'
