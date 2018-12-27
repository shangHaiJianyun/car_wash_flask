import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
# from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

from config import config_dict
from api.models.models import *

from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect

cache = Cache(config={'CACHE_TYPE': 'simple'})

# login_manager = LoginManager()
# login_manager.session_protection = 'strong'
# login_manager.login_view = 'login'


def setup_log(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_type):
    # 根据配置类型取出配置类
    config_class = config_dict[config_type]
    app = Flask(__name__)
    # 根据配置类来加载应用配置
    app.config.from_object(config_class)

    from flask_security import Security
    security = Security(app, datastore=user_datastore)
    cache.init_app(app)
    # session.init_app(app)

    # 调用flask_jwt_extended模块
    from api.common_func.decorators import jwt
    # jwt = JWTManager(app)
    jwt.init_app(app)

    # 对用户密码进行加解密的模块
    bcrypt = Bcrypt()
    bcrypt.init_app(app)

    from .modules.user import user_blu
    app.register_blueprint(user_blu, url_prefix="/api/user")

    from .modules.map import map_blu
    app.register_blueprint(map_blu, url_prefix="/api/map")

    from .modules.common import common_blu
    app.register_blueprint(common_blu, url_prefix="/api/common")


    # 配置日志文件
    setup_log(config_class.LOGLEVEL)

    from api.models.models import db
    db.init_app(app)

    # CSRFProtect(app)
    CORS(app)
    return app
