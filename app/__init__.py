import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import config

app = Flask(__name__)

if os.environ.get('HEROKU_ENV') is not None:
    app.config.from_object(config.ProductionConfig)

app.config.from_object(config.DevelopmentConfig)

db = SQLAlchemy(app)


from app import views, models


if __name__ == "__main__":
    print('loading')
    print(os.environ.get('DATABASE_URL'))
    port = int(os.environ.get('PORT', 5000))

    db.create_all()
    app.run(host='0.0.0.0', port=port)
