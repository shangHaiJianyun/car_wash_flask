# -*- coding: utf-8 -*-
# @Time    : 19-1-11 上午9:47
from api import Role, User


class UserM(object):
    def get(self, id):
        pass

    def get_all_user(self):
        users = User.query.all()
        return users

    def get_user_by_name(self, name):
        user = User.query.filter_by(username=name).first()
        return user

    def get_user_role(self, name):
        user_role = Role.query.filter_by(name=name).first()
        return user_role
