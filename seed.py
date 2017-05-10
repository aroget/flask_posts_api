from app import db
from app.models import Privilege
from sqlalchemy.exc import IntegrityError

DEFAULT_PRIVILEGES = [
    { 'name': 'read', 'level': 3 },
    { 'name': 'write', 'level': 2 },
    { 'name': 'manage', 'level': 1 }
]

def seed_privilege():
    for privilege in DEFAULT_PRIVILEGES:
        prv = Privilege(name=privilege['name'], level=privilege['level'])

        try:
            db.session.add(prv)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    return
