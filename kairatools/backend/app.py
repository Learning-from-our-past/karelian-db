import os

from flask import Flask, Blueprint
from flask_mail import Mail
from flask_restful import Api
from flask_security import Security, PeeweeUserDatastore
from kairatools.backend.features.flask_admin import setup_admin
from kairatools.backend.instance.config import app_config
from kairatools.backend.models.kairatools_models import User, Role, UserRole
from kairatools.backend.views.index import index_bp

import common.siirtokarjalaistentie_models as db_siirtokarjalaistentie_models
from common.db_connection import db_connection
from kairatools.backend.routes.usersroute import UserRoute


def get_app():
    # Load basic configurations
    config_name = os.getenv('APP_SETTINGS')  # config_name = "development"
    _app = Flask(__name__, instance_relative_config=True)
    _app.config.from_object(app_config[config_name])

    db_connection.init_database(app_config[config_name].DATABASE_NAME, app_config[config_name].DATABASE_USER)
    db_connection.connect()

    # Setup Kaira-db models
    db_siirtokarjalaistentie_models.set_database_to_models(db_connection.get_database())

    # Setup Rest-API
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)

    # Setup Flask-Mail
    mail = Mail(_app)

    # Setup Flask-Security
    user_datastore = PeeweeUserDatastore(db_connection.get_database(), User, Role, UserRole)
    security = Security(_app, user_datastore)

    # Setup Flask-Admin with Flask-Security
    setup_admin(_app, security)

    # Register route blueprints
    api.add_resource(UserRoute, '/user')
    _app.register_blueprint(api_bp)

    # Register view blueprints
    _app.register_blueprint(index_bp)

    return _app


if __name__ == '__main__':
    app = get_app()
    app.run()