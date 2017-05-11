import os

class Config(object):
    DEBUG = False

    SECRET_KEY = 'SOPA_DE_CARACOL'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/flask_demo'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class DevelopmentConfig(Config):
    DEBUG = True
