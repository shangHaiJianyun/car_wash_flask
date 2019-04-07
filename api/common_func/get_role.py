# -*- coding: utf-8 -*-
from api.models.models import Role


def get_user_role(name):
    user_role = Role.query.filter_by(name=name).first()
    return user_role
