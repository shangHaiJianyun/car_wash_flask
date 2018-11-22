"""
view for auth

"""
from flask import render_template, json, jsonify, request, abort, g
from flask import Blueprint, jsonify, request, current_app
# from flask_httpauth import HTTPBasicAuth
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required, roles_required, current_user

from model.models import *
# app = create_app()
# from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context
from flask import current_app

# app = Flask(__name__)
views = Blueprint('views_bp', __name__, template_folder='templates')
# auth = HTTPBasicAuth()


# auth with flask_httpauth
# @views.route("/")
# @auth.login_required
# def index():
#     print g.user, 'g.user', g.user.user_group
#     return jsonify({'user': g.user})


@views.route("/fsrole/")
@roles_required('cust_admin')
def flask_security_login2():
    u = row2dict(current_user)
    tk = current_user.get_auth_token()
    return jsonify({'user': u, 'token': tk})


# @views.route('/users', methods=['POST'])
# def new_user():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     ug = request.json.get('user_group')
#     if username is None or password is None:
#         # abort(400)  # missing arguments
#         return jsonify({'error': 'user name or password missing'})
#     if User.query.filter_by(username=username).first() is not None:
#         return jsonify({'error': 'user exists'})
#     user = User(username=username)
#     user_role = UserGroup.query.filter(UserGroup.name == ug).all()
#     user.user_group = user_role
#     user.hash_password(password)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({'username': user.username})


# flask -security
# @views.route('/users/create', methods=['POST'])
# def create_user():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     # ug_name = request.json.get('user_group')
#     user_datastore.create_user(username=username, password=password)
#     db.session.commit()
#     return jsonify({'username': username})

# @auth.verify_password
# def verify_password(username_or_token, password):
#     # print request.data, 'data'
#     # print request.authorization, 'au'
#     if request.path == "/views/api/login":
#         user = User.query.filter_by(username=username_or_token).first()
#         # print 'user', user
#         if not user or not user.verify_password(password):
#             return False
#     else:
#         user = User.verify_auth_token(username_or_token)
#         if not user:
#             return False
#     g.user = user
#     return True


# @views.route('/api/login')
# @auth.login_required
# def get_auth_token():
#     token = g.user.generate_auth_token()
#     return jsonify(token)
