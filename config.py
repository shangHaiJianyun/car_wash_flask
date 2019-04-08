# -*- coding: utf-8 -*-
import logging
import sys
import os
from datetime import timedelta

from redis import StrictRedis


class Config:
    DEBUG = True
    if sys.path[0] == '/home/chendebo/Desktop/car_wash_flask':
        # 本地测试用例数据库
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@localhost/car_wash'
    elif "DanielJiang" in os.getcwd():
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://jjh:jjhjjh100@localhost/car_wash?charset=utf8mb4'
        SQLALCHEMY_BINDS = {
            'sch': 'mysql+pymysql://jjh:jjhjjh100@localhost/sch?charset=utf8mb4'
        }
    else:
        # 服务器端数据库链接
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dev2:UpcTech2018@fueldev.c3qlqhbaxuou.rds.cn-north-1.amazonaws.com.cn/car_wash?charset=utf8mb4'

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SQLALCHEMY_ECHO = True
    # used for encryption and session management
    SECRET_KEY = 'mysecretkey'
    # 安全配置
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = '/uploads'

    # 设置jwt秘钥
    JWT_SECRET_KEY = 'super_key'
    PROPAGATE_EXCEPTIONS = True
    JWT_ACCESS_TOKEN_EXPIRES = False

    # SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
    # SECURITY_TOKEN_AUTHENTICATION_HEADER = 'auth_token'
    LOGGING_LEVEL = logging.DEBUG
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_TRACKABLE = False
    SECURITY_PASSWORD_SALT = 'upctech'
    SECURITY_USER_IDENTITY_ATTRIBUTES = 'username'
    # SECURITY_LOGIN_URL = '/user/login'  # 默认登陆模板
    SECURITY_TOKEN_MAX_AGE = 'None'  # never expired
    # REDIS_HOST = "127.0.0.1"  # redis的ip
    # REDIS_PORT = 6379  # redis的端口
    # SESSION_TYPE = "redis"  # session存储的数据库类型
    # SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置session存储使用的redis连接对象
    # SESSION_USE_SIGNER = True  # 对cookie中保存的sessionid进行加密(需要使用app的秘钥)
    # PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 设置session存储时间(session默认会进行持久化)

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_TASK_SERIALIZER = 'json'


class DevelopConfig(Config):  # 定义开发环境的配置
    DEBUG = True
    LOGLEVEL = logging.DEBUG


class ProductConfig(Config):  # 定义生产环境的配置
    DEBUG = False
    LOGLEVEL = logging.ERROR


# 设置配置字典
config_dict = {
    "dev": DevelopConfig,
    "pro": ProductConfig
}
