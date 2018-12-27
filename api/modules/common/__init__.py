# -*- coding: utf-8 -*-
# @Time    : 18-12-27 下午1:35
# @Author  : dbchen
# @File    : __init__.py.py

from flask import Blueprint

common_blu = Blueprint('common', __name__)

from .views import *
