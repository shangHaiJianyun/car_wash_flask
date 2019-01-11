import random
import ssl
import urllib.request

from flask import jsonify

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