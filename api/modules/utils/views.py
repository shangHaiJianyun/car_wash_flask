# -*- coding: utf-8 -*-
import random
import ssl
import urllib.request

from flask import jsonify, request

from api import app
from api.modules.utils import utils_blu


@utils_blu.route('/verify_mobile/<string:phone>/', methods=['GET'])
def get_verify_code(phone):
    '''
    短信 验证
    input:
        url: 'https://fesms.market.alicloudapi.com/sms'
        querys = 'code=12345678&phone=13547119500&skin=1'
        header('Authorization', 'APPCODE ' + "c8fe554fc33844a98ead645ea53eb7a6")
    return:
        verify code
    '''
    # phone = request.args.get('phone')
    code = str(random.randint(1000, 9999))
    host = 'https://fesms.market.alicloudapi.com'
    path = '/sms/'
    method = 'GET'
    appcode = 'd2b27069129f4ad9831b3ab4efc2f3b3'
    querys = 'code=' + code + '&phone=' + phone + '&skin=1'
    bodys = {}
    url = host + path + '?' + querys

    req = urllib.request.Request(url)
    req.add_header('Authorization', 'APPCODE ' + appcode)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    res = urllib.request.urlopen(req, context=ctx)
    content = res.read()
    rst = eval(content)
    if rst['Code'] == 'OK':
        return jsonify(dict(code=code))
    else:
        return jsonify(dict(code='0', error=rst['Code']))


@utils_blu.route('/help/', methods=['GET'])
def helps():
    """Print available route and functions."""
    func_list = []
    for rule in app.url_map.iter_rules():
        # print type(app.url_map.iter_rules()), app.url_map.iter_rules()
        if rule.endpoint != 'static':
            options = {}
            methods = [m for m in rule.methods]
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)
            func_list.append(dict(
                route=rule.rule, route_docs=app.view_functions[rule.endpoint].__doc__, route_methods=methods,
                route_args=options))
    func_list = sorted(func_list, key=lambda k: k['route'])
    # print func_list
    return jsonify(func_list)


# # celery测试接口
# @utils_blu.route('status/<task_id>')
# def task(task_id):
#     from api.celery_tasks.tasks import long_task
#     task = long_task.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         response = {'state': task.state, 'current': 0, 'total': 1}
#     elif task.state != 'FAILURE':
#         response = {'state': task.state, 'current': task.info.get('current', 0), 'total': task.info.get('total', 1)}
#         if 'result' in task.info:
#             response['result'] = task.info['result']
#     else:
#         response = {'state': task.state, 'current': 1, 'total': 1}
#
#     return jsonify(response)
#
