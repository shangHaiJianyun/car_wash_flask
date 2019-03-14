# -*- coding: utf-8 -*-
"""
manage.py
- provides a command line utility for interacting with the
  application to perform interactive debugging and setup
"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from api.common_func.area import AreaRateM, AreaM
from api.models.models import User, user_datastore
from api.common_func.get_role import get_user_role

from api import create_app, db

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
    user_datastore.create_role(name='User', description='Generic user role')
    user_datastore.create_role(name='Admin', description='Admin user role')
    user_datastore.create_role(name='Operate', description='Generic operate role')
    db.session.commit()
    # print('insert success')


@manager.command
def add_user():
    user = user_datastore.create_user(username='1', password='123')
    user.set_password()
    user_role = get_user_role('User')
    user_datastore.add_role_to_user(user, user_role)
    db.session.commit()
    # print('user generate')


@manager.command
def add_operate():
    user = user_datastore.create_user(username='2', password='123')
    user.set_password()
    user_role = get_user_role('Operate')
    user_datastore.add_role_to_user(user, user_role)
    db.session.commit()
    # print('operate generate')


@manager.command
def add_admin():
    user = user_datastore.create_user(username='admin', password='123')
    user.set_password()
    admin_role = get_user_role('Admin')
    user_datastore.add_role_to_user(user, admin_role)
    db.session.commit()
    # print('map generate')


@manager.command
def set_Arate():
    Area_rates = AreaRateM()
    Area_rates.add_new(name='一等', rate_level="A")
    Area_rates.add_new(name='二等', rate_level="B")
    Area_rates.add_new(name='三等', rate_level="C")
    Area_rates.add_new(name='交界处', rate_level="D")
    print('over')


@manager.command
def setArea():
    AreaM.set_area()


if __name__ == '__main__':
    manager.run()
