import datetime
import getpass
import sys

from flask_security.utils import hash_password
from kairatools.backend.app import get_app

from kairatools.backend.models.kairatools_models import User, Role, UserRole

with get_app().app_context():
    super_user = {
        'email': None,
        'password': None,
        'name': None,
        'active': True,
        'confirmed_at': datetime.datetime.now()
    }

    print('Please provide details of the new super user:')
    super_user['email'] = input('Email:')

    if not super_user['email']:
        print('Email is required!')
        sys.exit(1)

    super_user['password'] = hash_password(getpass.getpass())

    if not super_user['password']:
        print('Password is required!')
        sys.exit(1)

    super_user['name'] = input('Name (admin):') or 'admin'

    super_user_model = User(**super_user)
    super_user_model.save()

    # Set role to new user
    super_role = Role.get(Role.name == Role.default_roles['super'])

    super_user_user_role = UserRole(user_id=super_user_model.id, role_id=super_role.id)
    super_user_user_role.save()

    print('A new super user with email', super_user['email'], 'was created.')



