# -*- coding: utf-8 -*-
# @Time    : 18-12-27 下午1:35
# @Author  : dbchen
# @File    : __init__.py.py

from flask import Blueprint

utils_blu = Blueprint('utils', __name__)

from .views import *
