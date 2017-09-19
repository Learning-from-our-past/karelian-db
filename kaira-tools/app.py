from flask import Flask, Blueprint
from flask_security import Security, PeeweeUserDatastore
from instance.config import app_config
from flask_restful import Api
from models.kairatools_models import *
from routes.usersroute import UsersRoute
from flask_mail import Mail
from features.flask_admin import setup_admin
from views.index import index_bp
import os


# Load basic configurations
config_name = os.getenv('APP_SETTINGS')  # config_name = "development"
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(app_config[config_name])
app.config.from_pyfile('config.py')

# FIXME: Move these details to proper config file after everything else works ok
db_connection.init_database('learning-from-our-past', 'postgres')
db_connection.connect()

# Setup Rest-API
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Setup Flask-Mail
mail = Mail(app)

# Setup Flask-Security
user_datastore = PeeweeUserDatastore(db_connection.get_database(), User, Role, UserRole)
security = Security(app, user_datastore)

# Setup Flask-Admin with Flask-Security
setup_admin(app, security)

# Register route blueprints
api.add_resource(UsersRoute, '/users')
app.register_blueprint(api_bp)

# Register view blueprints
app.register_blueprint(index_bp)


if __name__ == '__main__':
    app.run()