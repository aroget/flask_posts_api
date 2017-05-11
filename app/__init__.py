import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import config

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)


from app import views, models
from app.utils.seed import seed_privilege

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))

    db.create_all()
    seed_privilege()
    app.run(host='0.0.0.0', port=port)
