from flask import jsonify, request, current_app, g, render_template, abort, session, redirect, url_for
from flask_security import roles_required, current_user, forms, auth_token_required, login_required
from flask_security.utils import login_user, logout_user

from start_project.common_func.get_role import get_user_role
from start_project.models import *
from start_project.modules.user import user_blu


# 主界面的显示
@user_blu.route("/")
@user_blu.route("/index")
@login_required
# @auth_token_required
@roles_required('Admin')
def index():
    token = request.args.get('auth_token')
    print(token)
    u = row2dict(current_user)
    # return render_templaxte('user/index.html', user=u)
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
    if user.password == password:
        token = user.get_auth_token()
        login_user(user)
        print(token)
        print(user.roles)
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
    return '退出登陆'


# 添加新用户
@user_blu.route('/add_user', methods=['POST'])
@roles_required('Admin')
@login_required
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User()
    user.mobile = username
    user.password = password
    user_role = get_user_role('User')
    user_datastore.add_role_to_user(user, user_role)
    db.session.commit()

    return jsonify({'status': 'add success'})


# 修改密码/需要手机号短信验证
@user_blu.route('/change_pwd', methods=['GET', 'POST'])
@login_required  # 只有登录的人才能修改密码
def change_password():
    # TODO:验证码的验证
    old_pwd = request.json.get('password')
    new_pwd = request.json.get('new_password')
    if current_user.password == old_pwd:
        current_user.password = new_pwd
        # 修改密码
        db.session.add(current_user)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return jsonify({"error": "error password"})


@user_blu.route('/api')
# @auth_token_required
@roles_required('Admin')
def token_protected():
    return 'you\'re logged in by Token!'
