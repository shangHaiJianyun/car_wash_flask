# import functools
# from flask import session, current_app, g
#
# from role_allocate import User
#
#
# # 查询用户登录状态
# def user_login_data(f):
#     @functools.wraps(f)  # 可以让闭包函数wrapper使用指定函数f的函数信息 (如函数名wrapper.__name__  文档注释__doc__)
#     def wrapper(*args, **kwargs):
#         # 判断用户是否登录
#         user_id = session.get("user_id")
#         user = None
#         if user_id:
#             # 根据user_id查询用户模型
#             try:
#                 user = User.query.get(user_id)
#             except BaseException as e:
#                 current_app.logger.error(e)
#
#         g.user = user  # 让g变量记录查询出的用户数据
#
#         # 再执行原有功能
#         return f(*args, **kwargs)
#
#     return wrapper
