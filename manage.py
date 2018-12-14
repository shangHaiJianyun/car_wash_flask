# -*- coding: utf-8 -*-
"""
manage.py
- provides a command line utility for interacting with the
  application to perform interactive debugging and setup
"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from api.common_func.get_role import get_user_role
from api.models.models import db, Role, User, roles_users, user_datastore
from api.modules.admin.views import *

from api import create_app
app = create_app("dev")

migrate = Migrate(app, db)
manager = Manager(app)

# provide a migration utility command
manager.add_command('db', MigrateCommand)


# enable python shell with application context


@manager.shell
def shell_ctx():
    return dict(app=app,
                db=db,
                )


if __name__ == '__main__':

    manager.run()
    # initrole()
    # add_test_user()
