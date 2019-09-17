# -*- coding: utf-8 -*-
import re
import random

from flask import jsonify, request, current_app, g, render_template, abort, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_security import current_user, forms, auth_token_required, login_required
from flask_security.utils import login_user, logout_user

from api.common_func.decorators import admin_required, roles_required
from api.common_func.get_role import get_user_role
from api.models.models import *
from api.modules.user import user_blu


# 主界面的显示
@user_blu.route("/")
@user_blu.route("/index")
@login_required
@jwt_required
def index():
    user = current_user
    # user = get_jwt_identity()
    u = row2dict(user)
    # return jsonify(user)
    return jsonify(u)


# 用户登陆
@user_blu.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    try:
        user = User.query.filter_by(username=username).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(msg="db error")
    if not user:
        return jsonify(msg='Not found this user')
    if user.check_password(password):
        token = create_access_token(identity=username)
        login_user(user)
        # print(token)
        # print(user.roles)
        data = {
            "token": token,
            'username': user.username,
            "user_role": str(user.roles)
        }
        # print("密码成功")
        return jsonify(data)
    else:
        return jsonify(msg="Password error")


# 用户登出
@user_blu.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(msg='user logout')


# 添加新用户，只有Admin角色才可进行操作
@user_blu.route('/add_user', methods=['POST'])
# @login_required
# @admin_required
def add_user():
    # 定义装饰器admin_required管理操作权限
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('user_role')
    user = user_datastore.create_user(username=username, password=password)
    user.set_password()
    user_role = get_user_role(role)
    user_datastore.add_role_to_user(user, user_role)
    user.mobile = username
    db.session.commit()

    return jsonify(msg='add success')


# 修改并更新用户资料
@user_blu.route('/update_info', methods=['POST'])
@login_required
def update_info():
    # 获取需要的参数
    name = request.json.get('name')
    email = request.json.get('email')
    mobile = request.json.get('mobile')
    # 校验参数的完整性
    if not all([mobile, name, email]):
        return jsonify(msg='please check your parameters')
    # 校验邮箱格式
    if not re.match('[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',email):
        return jsonify(msg='wrong email')
    # 校验手机号格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(msg='illegal mobile')

    # 修改用户信息
    current_user.name = name
    current_user.email = email
    current_user.mobile = mobile
    db.session.commit()

    return jsonify(row2dict(current_user))


# 修改密码/需要手机号短信验证
@user_blu.route('/change_pwd', methods=['GET', 'POST'])
@login_required  # 只有登录的人才能修改密码
def change_password():
    # 获取参数
    new_password = request.json.get('password')

    current_user.password = new_password
    current_user.set_password()
    db.session.commit()
    return jsonify(msg='modify success')


# token携带后验证
@user_blu.route('/protected', methods=['GET'])
# @jwt_required
# @admin_required
@roles_required('User')
def token_protected():
    this_user = get_jwt_identity()
    return jsonify(logged_in_as=this_user), 200
    # return 'you\'re logged in by Token!'



def weixin_url(client_id, redirect_url):
    """
    WEIXIN URL
    :param client_id: your weixin appID
    :param redirect_url: your weixin redirect_url
    :return: WEIXIN URL
    """
    weixin = "https://open.weixin.qq.com/connect/qrconnect?appid={client_id}&redirect_uri={redirect_uri}\
    &response_type=code&scope=SCOPE&state=STATE#wechat_redirect".format(
        client_id=client_id, redirect_uri=redirect_url
    )
    return weixin


def weixin(client_id, client_secret, code):
    """
    weixin登录
    :param client_id: appID
    :param client_secret: appSecret
    :param code: 从WEIXIN服务器得到code
    :return: 返回所用信息
    """
    get_access_token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    # 请求得到access_token

    response = requests.get(url=get_access_token_url, params={
        'appid': client_id,
        'secret': client_secret,
        'code': code
    }).text
    # 获取openid
    response_open_id = json.loads(response)
    open_id = response_open_id['openid']
    return open_id
