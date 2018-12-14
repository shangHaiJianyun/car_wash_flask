# -*- coding:utf-8 -*-
from api.common_func.get_role import get_user_role
from api.models.models import user_datastore, db


def initrole():
    user_datastore.create_role(name='User',description='Generic user role')
    user_datastore.create_role(name='Operate', description='Generic operate role')
    user_datastore.create_role(name='Admin',description='Admin user role')
    db.session.commit()
    # print('insert success')


def add_test_user():
    user = user_datastore.create_user(username='18355096167',password='1234567')
    user_role = get_user_role('User')
    user_datastore.add_role_to_user(user,user_role)
    db.session.commit()
    # print('user generate')

    user = user_datastore.create_user(username='12345678', password='1234567')
    admin_role = get_user_role('Admin')
    user_datastore.add_role_to_user(user, admin_role)
    db.session.commit()
    # print('admin generate')
