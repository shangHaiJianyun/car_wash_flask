# -*- coding: utf-8 -*-
# @Time    : 19-1-4 下午1:18
from flask import Blueprint

lpr_blu = Blueprint('lpr', __name__)

from .views import *
