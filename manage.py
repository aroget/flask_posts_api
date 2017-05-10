from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import db, app
from seed import seed_privilege

migrate = Migrate(app, db)

app.debug = True
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    seed_privilege()
    manager.run()