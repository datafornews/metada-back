import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app import app, db
from app.models import *


app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(use_ipython=True))


if __name__ == '__main__':
    # 1st step : python manage.py db init
    # 2nd step : python manage.py db migrate
    # 3rd step : python manage.py db upgrade
    # HEROKU : heroku run python manage.py db upgrade --app 
    # no migrate if migrations run and commited
    manager.run()