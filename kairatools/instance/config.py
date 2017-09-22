import os


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('PASSWORD_SALT')

    # The registration should be activated by admin. Let anyone to request registration, but
    # allow access only after the request is confirmed by admin
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_CONFIRMABLE = True
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True

    # Use gmail for development
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    SECURITY_EMAIL_SENDER = os.getenv('MAIL_USERNAME')

    # Database
    DATABASE_NAME = 'learning-from-our-past'
    DATABASE_USER = 'postgres'


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    DEBUG = True

    # Database
    DATABASE_NAME = 'karelian_testdb'
    DATABASE_USER = 'postgres'


class CIConfig(TestingConfig):
    # Set these properties here since they are used only in CI tests and it's not needed to pass
    # them via environment there. Just export APP_SETTINGS=ci in travis config file.
    SECRET_KEY = 'secret'
    SECRET = 'secret'
    SECURITY_PASSWORD_SALT = 'testsalt'
    MAIL_USERNAME = 'test@example.com'
    MAIL_PASSWORD = 'password'


class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'ci': CIConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}
