"""
view for flask-security auth

"""
from flask import render_template, json, jsonify, request, abort, g
from flask import Blueprint, jsonify, request, current_app
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, roles_required, current_user, utils

from model.models import *
# app = create_app()
# from flask_httpauth import HTTPBasicAuth
# from passlib.apps import custom_app_context
# from flask import current_app

# app = Flask(__name__)
auth_bp = Blueprint('auth_bp', __name__, template_folder='templates')


@auth_bp.route("/get_user/")
@login_required
def current_user_info():
    u = row2dict(current_user)
    roles = current_user.roles
    r = [row2dict(x) for x in roles]
    return jsonify({'user': u, 'roles': r})


@auth_bp.route("/fsrole/")
@roles_required('cust_admin')
def flask_security_login2():
    u = row2dict(current_user)
    tk = current_user.get_auth_token()
    return jsonify({'user': u, 'token': tk})


@auth_bp.route('/users/create', methods=['POST'])
def create_user():
    username = request.json.get('username')
    password = request.json.get('password')
    # ug_name = request.json.get('user_group')
    r = user_datastore.create_user(username=username, password=password)
    db.session.commit()
    return jsonify({'status': 'success', 'user': row2dict(r)})


@auth_bp.route('/logout')
def logout():
    utils.logout_user()
    return jsonify({'status': 'success'})