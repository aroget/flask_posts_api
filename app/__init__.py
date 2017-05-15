import os
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy

from app import config

app = Flask(__name__)
CORS(app)

if os.environ.get('HEROKU_ENV') is not None:
    app.config.from_object(config.ProductionConfig)

if os.environ.get('HEROKU_ENV') is None:
    app.config.from_object(config.DevelopmentConfig)

db = SQLAlchemy(app)


from app import views, models


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    db.create_all()
    app.run(host='0.0.0.0', port=port)
