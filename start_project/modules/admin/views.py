# from flask import Blueprint, render_template, jsonify
# from flask import current_app, redirect, request, url_for
# from role_allocate.models import db, row2dict, user_datastore
# from role_allocate.models import User
# from flask_security import roles_required, login_required, current_user, login_user, auth_token_required
#
# from role_allocate.modules.admin import admin_blu
#
#
# @admin_blu.route('/')
# @roles_required('Admin')
# @login_required
# def index():
#     u = row2dict(current_user)
#     return render_template('admin/admin_index.html', users=u)

#
# @admin_blu.route('/login', methods=['POST'])
# def login():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     try:
#         obj = User.query.filter_by(username=username).first()
#     except BaseException as e:
#         current_app.logger.error(e)
#         return jsonify({"error": "Database error"})
#     if not obj:
#         return jsonify({'error': 'Not found this user'})
#     if obj.verify_password(password):
#         token = obj.get_auth_token()
#         login_user(obj)
#         return jsonify({'token': token}, {'status': 'Login success'})
#     else:
#         return jsonify({"error": "Password error"})


