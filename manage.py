# -*- coding: utf-8 -*-
"""
manage.py
- provides a command line utility for interacting with the
  application to perform interactive debugging and setup
"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from role_allocate.common_func.get_role import get_user_role
from role_allocate.models import db, Role, User, roles_users, user_datastore

from role_allocate import create_app
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


@manager.command
def initrole():
    user_datastore.create_role(name='User',description='Generic user role')
    user_datastore.create_role(name='Operate', description='Generic operate role')
    user_datastore.create_role(name='Admin',description='Admin user role')
    db.session.commit()
    print('insert success')


@manager.command
def create_user():
    user = user_datastore.create_user(username='18355096167',password='1234567')
    user_role = get_user_role('User')
    user_datastore.add_role_to_user(user,user_role)
    db.session.commit()
    print('user generate')


@manager.command
def create_admin():
    user = user_datastore.create_user(username='12345678', password='1234567')
    admin_role = get_user_role('Admin')
    user_datastore.add_role_to_user(user, admin_role)
    db.session.commit()
    print('admin generate')


@manager.command
def create_operate():
    pass

if __name__ == '__main__':
    manager.run()
    # add_test_users()
