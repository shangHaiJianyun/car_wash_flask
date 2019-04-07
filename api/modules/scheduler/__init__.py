# -*- coding: utf-8 -*-
from flask import Blueprint

# 1. 创建蓝图对象
sch_blu = Blueprint("sch", __name__)

from .views import *
# from .sch import *
# from .sch_sim import *
