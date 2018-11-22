# -*- coding: UTF-8 -*-
"""
application.py
- creates a Flask app instance and registers the database object
"""
import logging
from flask import Flask
# from flask_httpauth import HTTPBasicAuth
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask_cors import CORS
from model.models import *
from mycache import cache
import os


def create_app(app_name='Fuel_API'):
    app = Flask(app_name)
    if "DanielJiang" in os.getcwd():
        app.config.from_object('api.config.BaseConfig')
    else:
        app.config.from_object('api.config.ProductionConfig')
    CORS(app)

    handler = logging.FileHandler(app.config['LOGGING_LOCATION'], encoding='UTF-8')
    handler.setLevel(app.config['LOGGING_LEVEL'])
    formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
    handler.setFormatter(formatter)
    app.logger.setLevel(app.config['LOGGING_LEVEL'])
    app.logger.addHandler(handler)

    security = Security(app, user_datastore)

    cache.init_app(app)

    from api import api
    app.register_blueprint(api, url_prefix="/api/wxapi")

    from client_api import client_api
    app.register_blueprint(client_api, url_prefix="/api/client_api")


    from share_api import share_api
    app.register_blueprint(share_api, url_prefix="/api/share_api")

    from views import views
    app.register_blueprint(views, url_prefix="/api/views")

    from fs_auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/fs_auth")

    from page import page
    app.register_blueprint(page, url_prefix="/api/page")

    from company_api import company_api
    app.register_blueprint(page, url_prefix="/api/company_api")

    from model.models import db
    db.init_app(app)

    return app
