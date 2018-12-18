import re
import random

from flask import jsonify, request, current_app, g, render_template, abort, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_security import roles_required, current_user, forms, auth_token_required, login_required
from flask_security.utils import login_user, logout_user

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


# @app.route('/user/register', methods=['GET', 'POST'])
# def register():
#     form = forms.RegisterForm()
#     if form.validate_on_submit():
#         if form.password.data != form.password_again.data:
#             errors = '两次输入的密码不同'
#             return render_template('register.html', form=form, errors=errors)
#         new_user = user_datastore.create_user(email=form.email.data, password=form.password.data)
#         normal_role = user_datastore.find_role('User')
#         db.session.add(new_user)
#         user_datastore.add_role_to_user(new_user, normal_role)
#         login_user(new_user)
#         return redirect(url_for('index'))
#     return render_template('register.html', form=form)


# # 用户注册
# @user_blu.route('/user/register', methods=['POST'])
# def register():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     if username is None or password is None:
#         # abort(400)  # missing arguments
#         return jsonify({'error': 'Request not Json or miss name/pwd'})
#     if User.query.filter_by(username=username).first() is not None:
#         return jsonify({'error': 'User is already existed.'})
#     user = User(username=username)
#     user.hash_password(password)
#     try:
#         db.session.add(user)
#         db.session.commit()
#         login_user(user)
#     except BaseException as e:
#         current_app.logger.error(e)
#         db.session.rollback()  # 设置回滚
#         return jsonify({"error": "Database error"})
#     return jsonify({'username': user.username})


# 用户登陆
@user_blu.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    try:
        user = User.query.filter_by(username=username).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify({"error": "Database error"})
    if not user:
        return jsonify({'error': 'Not found this user'})
    if user.check_password(password):
        token = user.get_auth_token()
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
        return jsonify({"error": "Password error"})


# 用户登出
@user_blu.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify(message='user logout')


# 添加新用户，只有Admin角色才可进行操作
@user_blu.route('/add_user', methods=['POST'])
@login_required
def add_user():
    # TODO：定义装饰器admin_required管理操作权限
    username = request.json.get('username')
    password = request.json.get('password')
    user = user_datastore.create_user(username=username, password=password)
    user.set_password()
    user_role = get_user_role('User')
    user_datastore.add_role_to_user(user, user_role)
    user.mobile = username
    db.session.commit()

    return jsonify({'status': 'add success'})


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
        return jsonify(error='please check your parameters')
    # 校验邮箱格式
    if not re.match('[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$',email):
        return jsonify(error='wrong email')
    # 校验手机号格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(error='illegal mobile')

    # 修改用户信息
    current_user.name = name
    current_user.email = email
    current_user.mobile = mobile
    db.session.commit()

    return jsonify(row2dict(current_user))


# 获取短信验证码
@user_blu.route('/get_sms_code', methods=['POST'])
def get_sms_code():
    # 获取参数  request.json可以获取到application/json格式传过来的json数据
    mobile = request.json.get("mobile")
    # 校验参数
    if not mobile:
        return jsonify(errno='PARAMERR error')

    # 校验手机号格式
    if not re.match(r"1[35678]\d{9}$", mobile):
        return jsonify(errno='error')

    # 根据图片key取出验证码文字
    # try:
    #     real_img_code = sr.get("img_code_id_" + img_code_id)
    # except BaseException as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno='DBERROR')

    # 如果校验成功, 发送短信
    # 生成4位随机数字
    sms_code = "%04d" % random.randint(0, 9999)
    current_app.logger.info("短信验证码为: %s" % sms_code)
    # res_code = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    # if res_code == -1:  # 短信发送失败
    #     return jsonify(errno=RET.THIRDERR, errmsg=error_map[RET.THIRDERR])

    # # 将短信验证码保存到redis
    # try:
    #     sr.set("sms_code_id_" + mobile, sms_code, ex=60)
    # except BaseException as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=' DBERROR')
    # 将短信发送结果使用json返回
    return jsonify(erro='OK')

# 修改密码/需要手机号短信验证
@user_blu.route('/change_pwd', methods=['GET', 'POST'])
@login_required  # 只有登录的人才能修改密码
def change_password():
    # TODO:验证码的验证
    mobile = request.json.get('mobile')
    cur_user = get_jwt_identity()
    if cur_user.mobile == mobile:

        # 如果校验成功, 发送短信
        # 生成4位随机数字
        sms_code = "%04d" % random.randint(0, 9999)
        current_app.logger.info("短信验证码为: %s" % sms_code)
        # res_code = CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # if res_code == -1:  # 短信发送失败
        #     return jsonify(erro='THIRDERR')

        # 将短信验证码保存到redis
        # try:
        #     sr.set("sms_code_id_" + mobile, sms_code, ex=60)
        # except BaseException as e:
        #     current_app.logger.error(e)
        #     return jsonify(erro='DB ERROR')
        # 将短信发送结果使用json返回
        return jsonify(error='did it')


# token携带后验证
@user_blu.route('/protected', methods=['GET'])
@jwt_required
def token_protected():
    this_user = get_jwt_identity()
    return jsonify(logged_in_as=this_user), 200
    # return 'you\'re logged in by Token!'
