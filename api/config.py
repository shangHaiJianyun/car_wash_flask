# -*- coding: utf-8 -*-
"""
config.py  
- settings for the flask application object
"""
import logging


class BaseConfig(object):
    ENV = 'develop'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://jjh:jjhjjh100@localhost/car_sch'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # used for encryption and session management
    SECRET_KEY = 'mysecretkey'
    # 安全配置
    CSRF_ENABLED = True
    UPLOAD_FOLDER = '/uploads'

    LOGGING_LOCATION = 'log/app.log'
    LOGGING_FORMAT = '%(asctime)s  - in Module %(module)s: - Func %(funcName)s  - Line: %(lineno)s - %(message)s'

    LOGGING_LEVEL = logging.DEBUG
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_TRACKABLE = False
    SECURITY_PASSWORD_SALT = 'upctech'
    SECURITY_USER_IDENTITY_ATTRIBUTES = 'username'
    SECURITY_LOGIN_URL = '/api/login'
    SECURITY_TOKEN_MAX_AGE = 'None'  # never expired


class ProductionConfig(BaseConfig):
    ENV = 'production'
    DEBUG = False    
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Nopwd@localhost/car_sch'
    LOGGING_LEVEL = logging.ERROR


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
