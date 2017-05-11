import os

class Config(object):
    DEBUG = False

    SECRET_KEY = 'SOPA_DE_CARACOL'

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://bd890f399d8ceb:bea739ec@us-cdbr-iron-east-03.cleardb.net/heroku_3fe77ae70ca22b5"

class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/flask_demo'
