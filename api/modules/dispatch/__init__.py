# -*- coding: utf-8 -*-
# @Time    : 19-3-5 上午10:04

from flask import Blueprint

dis_blu = Blueprint('dis', __name__)

from .views import *