# -*- coding: UTF-8 -*-
"""
api.py
- provides the API endpoints for wx
  REST requests and responses

cache:
https://pythonhosted.org/Flask-Cache/

"""

from flask import Blueprint, jsonify, request, current_app, abort, g
from flask import redirect, url_for
from model.models import *
# from flask_httpauth import HTTPBasicAuth
# from passlib.apps import custom_app_context
from views import *
import hashlib
import requests
import time
import os
import os.path
import random
import urllib
from wxhelper import WxClient
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from mycache import cache
from wxconfig import *


wxclient = WxClient(APP_ID, APP_SECRET)

# SITEURL = 'http://donation.i568.me/'

# with app.app_context():
#     cache = Cache()
#     cache.init_app(app, config={'CACHE_TYPE': 'simple'})

api = Blueprint('api', __name__)

# cache.init_app(app, config={'CACHE_TYPE': 'simple'})
# cache = Cache(config={'CACHE_TYPE': 'simple'})


@api.route('/help/', methods=['GET'])
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
                route=rule.rule, route_docs=app.view_functions[rule.endpoint].__doc__, route_methods=methods, route_args=options))
    func_list = sorted(func_list, key=lambda k: k['route'])
    # print func_list
    return jsonify(func_list)


@api.route('/wx/', methods=['GET', 'POST'])
def wx():
    '''
     微信 公众号 接口 url
    '''
    if request.method == "GET":
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        token = TOKEN
        list = [token, timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, list)
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            reply = echostr
        else:
            reply = 'error'
    else:
        data = request.data
        reply = process_msg(data)
        # reply = url_for('api.wx_token', _external=True)
    return reply


@api.route('/wx/get_token/', methods=['GET'])
@cache.cached(timeout=300)
def wx_token():
    '''
        get and save token in cache
    '''
    ctime = int(time.time())
    wxclient = Client(APP_ID, APP_SECRET)
    wx_token = wxclient.grant_token()['access_token']
    js_url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket"
    param = {"access_token": wx_token, "type": "jsapi"}
    js_ticket = requests.get(js_url, params=param).json()
    time_s = ctime
    return jsonify(dict(access_token=wx_token, time_s=time_s, timestamp=time_s, js_ticket=js_ticket['ticket']))


def process_msg(data):
    '''
        process message get

    '''
    tree = ET.fromstring(data)
    result = dict((child.tag, (child.text))
                  for child in tree)
    msgtype = result['MsgType']
    user_id = result['FromUserName']
    wx_token = wx_token()['access_token']
    r = wxclient.get_user_info(user_id, wx_token)
    nickname = ''
    if 'nickname' in r:
        nickname = r['nickname'].encode('utf8')
    result.update(nickname=nickname)
    if msgtype == "event":
        event_article = process_event(result)
        return event_article
    elif msgtype == 'text':
        return process_text_msg(result)
    else:
        return reply_text_message(user_id, '谢谢您再次关注')


def process_event(result):
    '''
        1 关注/取消关注事件
        2 扫描带参数二维码事件
        3 上报地理位置事件
        4 自定义菜单事件
        5 点击菜单拉取消息时的事件推送
        6 点击菜单跳转链接时的事件推送
    '''
    user_id = result['FromUserName']
    nickname = result['nickname']
    event = result['Event']
    if (event == 'CLICK'):
        clickkey = result['EventKey'].upper()
        # article = event_click_article(user_id, clickkey)
        return process_click(result)
        # return reply_article(user_id, article)
    elif (event == 'subscribe'):
        event_key = result['EventKey']
        article = process_subscribe(0, user_id, nickname)
        return reply_article(user_id, article)
        # return register_user(user_id)
#       data = article_data_for_newuser(user_id)
        # return reply_article(user_id, article)
    elif event == 'VIEW':
        return process_view(result)
    if event == 'SCAN':
        scan_key = result['EventKey']
        article = process_scan(result)
        return reply_article(user_id, article)
    else:
        article = default_article()
        return reply_article(user_id, article)


def process_subscribe(ref_user, wxid, nickname):
    '''
        处理关注事件
        1. 新用户
        user_type = ['doctor', 'stores', 'patient', 'dist', 'sales', 'internal']


    '''
    welcome_content = "欢迎关注  " + WX_NAME
    newuser_url = url_for('api.wx_token', _external=True)
    welcome_newuser_article = [
        {
            "Title": "欢迎关注！！！！",
            "Description": welcome_content + nickname + "",
            "PicUrl": "",
            "Url": newuser_url},
    ]
    return welcome_newuser_article


def process_scan(result):
    '''
        处理已关注用户的扫描事件
        1. 取得 扫描的 scene_str
          event-event_id
          client-client_id
    '''
    wxid = result['FromUserName']
    scan_key = result['EventKey']
    nickname = result['nickname']
    article = default_article
    return article


def reply_text_message(user_id, content):
    """ reply xml message"""
    textTpl = """<xml><ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content></xml>"""
    echostr = textTpl % (user_id, WXID, int(time.time()), content)
    # MsgType : text :自动回复； transfer_customer_service：转发给客服
    return echostr


def default_article():
    # link_url = URL('wx_shop', 'index', scheme=True, host=True)
    article = [
        {
            "Title": "欢迎关注 " + WX_NAME,
            "Description": "欢迎关注 " + WX_NAME,
            "PicUrl": "",
            "Url": ''},
    ]
    return article


def reply_artical_message(user_id, content):
    """ reply xml message"""
    pictextTpl = """<xml>
            <ToUserName><![CDATA[%s]]></ToUserName>
            <FromUserName><![CDATA[%s]]></FromUserName>
            <CreateTime>%s</CreateTime>
            <MsgType><![CDATA[news]]></MsgType>
            <ArticleCount>2</ArticleCount>
            <Articles>
            <item>
            <Title><![CDATA[title1]]></Title>
            <Description><![CDATA[description1]]></Description>
            <PicUrl><![CDATA[http://tp4.sinaimg.cn/1407979163/180/5629690180/1]]></PicUrl>
            <Url><![CDATA[http://ctrip.com]]></Url>
            </item>
            <item>
            <Title><![CDATA[jd]]></Title>
            <Description><![CDATA[jd1]]></Description>
            <PicUrl><![CDATA[http://misc.360buyimg.com/lib/img/e/logo-201305.png]]></PicUrl>
            <Url><![CDATA[http://jd.com]]></Url>
            </item>
            </Articles>
            </xml>
          """
    echostr = pictextTpl % (user_id, WXID, str(int(time.time())))
    return echostr


def reply_article(user_id, article1):
    TEMPLATE = """<xml>
    <ToUserName><![CDATA[{target1}]]></ToUserName>
    <FromUserName><![CDATA[{source}]]></FromUserName>
    <CreateTime>{time}</CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>{count}</ArticleCount>
    <Articles>{items}</Articles>
    </xml>"""
    ITEM_TEMPLATE = """<item>
    <Title><![CDATA[{title}]]></Title>
    <Description><![CDATA[{description}]]></Description>
    <PicUrl><![CDATA[{picurl}]]></PicUrl>
    <Url><![CDATA[{url}]]></Url>
    </item>"""
    items = []
    for a in article1:
        items.append(ITEM_TEMPLATE.format(
            title=a['Title'],
            description=a['Description'],
            picurl=a['PicUrl'],
            url=a['Url']
        ))
    l = len(items)
    r = []
    r.append(TEMPLATE.format(
        target1=user_id,
        source=WXID,
        time=str(int(time.time())),
        count=l,
        items=''.join(items)
    ))
    # lgresult(user_id, r[0])
    return r[0]


def create_article(user_id, data, userinfo):
    """
        create article from data
    """
    article = []
    r = data
    l = len(r)
    if l > 3:
        l = 3
    for i in xrange(0, l):
        d = {'Title': 'Title',
             'Description': 'Desc',
             'PicUrl': URL('download', args='picUrl', scheme=True, host=True),
             'Url': 'URL'
             }
        article.append(d)
    return article


def create_qr(expirt_sec, action_name, scene_str):
    '''
        create wechat qr
        action_name = QR_LIMIT_STR_SCENE or QR_STR_SCENE
        return qrticket
    '''
    wx_token = wx_wx_token()['access_token']
    url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=" + wx_token
    data = {'expire_seconds': expirt_sec, 'action_name': action_name,
            'action_info': {'scene': {'scene_str': scene_str}}}
    re = requests.post(url, data=json.dumps(data)).json()
    qr_ticket = re['ticket']
    return dict(qr_ticket=qr_ticket)


def create_qr_lim(scene_str):
    '''
        create wechat qr limited
        QR_LIMIT_STR_SCENE
        return qrticket
    '''
    wx_token = wx_token()['access_token']
    url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=" + wx_token
    data = {'action_name': 'QR_LIMIT_STR_SCENE',
            'action_info': {'scene': {'scene_str': scene_str}}}
    re = requests.post(url, data=json.dumps(data)).json()
    qr_ticket = re['ticket']
    return dict(qr_ticket=qr_ticket)
