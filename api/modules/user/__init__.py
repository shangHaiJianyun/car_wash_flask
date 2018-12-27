from flask import Blueprint

# 1. 创建蓝图对象
user_blu = Blueprint("user", __name__)

# 4. 关联视图函数
from .views import *
