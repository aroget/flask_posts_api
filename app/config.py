import os

DEBUG = True

if os.environ.get('HEROKU_ENV') is None:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/flask_demo'


SECRET_KEY = 'SOPA_DE_CARACOL'

SQLALCHEMY_TRACK_MODIFICATIONS = True
