# -*- coding: utf-8 -*-
import logging
import os
from datetime import timedelta

from redis import StrictRedis


class Config:
    DEBUG = True
    if 'chendebo' in os.getcwd():
        # 本地测试用例数据库
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@localhost/car_wash'
    elif "DanielJiang" in os.getcwd():
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://jjh:jjhjjh100@localhost/car_wash?charset=utf8mb4'
        SQLALCHEMY_BINDS = {
            'sch': 'mysql+pymysql://jjh:jjhjjh100@localhost/sch?charset=utf8mb4'
        }
    else:
        # 服务器端数据库链接
        # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dev2:UpcTech2018@fueldev.c3qlqhbaxuou.rds.cn-north-1.amazonaws.com.cn/car_wash?charset=utf8mb4'
        # 测试
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dev2:UpcTech2018@upcnxdb.cifgk3opujie.rds.cn-northwest-1.amazonaws.com.cn/test_cw_backend ?charset=utf8mb4'
        # 上线
        # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://dev2:UpcTech2018@upcnxdb.cifgk3opujie.rds.cn-northwest-1.amazonaws.com.cn/cw_backend ?charset=utf8mb4'

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

    LOGGING_LEVEL = logging.DEBUG
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_TRACKABLE = False
    SECURITY_PASSWORD_SALT = 'upctech'
    SECURITY_USER_IDENTITY_ATTRIBUTES = 'username'
    SECURITY_TOKEN_MAX_AGE = 'None'  # never expired

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_TASK_SERIALIZER = 'json'
    # 定时任务
    CELERYBEAT_SCHEDULE = {

        'change_order_status': {
            'task': 'api.celery_tasks.tasks.change_order_status',
            'schedule': timedelta(seconds=60),
            'args': ''
        },
        'sch_today': {
            'task': 'api.celery_tasks.tasks.sch_today_orders',
            'schedule': timedelta(seconds=3600),
            'args': ''
        },
        'sch_tomorrow': {
            'task': 'api.celery_tasks.tasks.sch_tomorrow_orders',
            'schedule': timedelta(seconds=3600),
            'args': ''
        }
    }


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
