# -*- coding: UTF-8 -*-
"""
client_api.py
- provides the API endpoints for consuming and producing
  REST requests and responses
"""

from flask import Blueprint, jsonify, request, current_app, abort, g
from model.models import *
# from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context
from views import *
from controllers.user_client import *
from controllers.vehicle_fuel import *
import requests
from wxconfig import *

client_api = Blueprint('client_api', __name__)


@client_api.route('/client/get_xcxid/', methods=['GET'])
def get_xcxid():
    '''
        xcx wx.login()  得到 code
        input:
            code: 小程序 wx.login 获得的 code,
        output:  xcxid, userInfo
    '''
    code = request.args.get('code')
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': XCX_APPID,
        'secret': XCX_SECRET,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    r = requests.get(url, params=params).json()
    return jsonify(r)


@client_api.route('/client/get_user_xcx/', methods=['GET'])
def check_user():
    '''
        input:
            xcxId: 
        output:  xcxid, userInfo
    '''
    # code = request.args.get('code')
    # url = 'https://api.weixin.qq.com/sns/jscode2session'
    # params = {
    #     'appid': XCX_APPID,
    #     'secret': XCX_SECRET,
    #     'js_code': code,
    #     'grant_type': 'authorization_code'
    # }
    # r = requests.get(url, params=params).json()
    xcxId = request.args.get('xcxId')
    clients = ClientsM()
    userInfo = clients.get_client_by_xcxid(xcxId)
    return jsonify(dict(xcxId=xcxId, userInfo=userInfo))


@client_api.route('/client/get_user_by_code/', methods=['GET'])
def check_user_by_code():
    '''
        input:
            code: 小程序 wx.login 获得的 code,
        output:  xcxid, userInfo
    '''
    code = request.args.get('code')
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': XCX_APPID,
        'secret': XCX_SECRET,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    r = requests.get(url, params=params).json()
    if 'openid' in r:
        xcxId = r['openid']
        unionid = r['unionid']
        clients = ClientsM()
        userInfo = clients.get_client_by_xcxid(xcxId)
        if userInfo:
            return jsonify(dict(xcxId=xcxId, userInfo=userInfo, unionid=unionid, s_key=r['session_key']))
        else:
            return jsonify(dict(xcxId=xcxId, userInfo={}, unionid=xcxId, s_key=r['session_key']))
    else:
        return jsonify(dict(xcxId='', userInfo={}, unionid=''))


@client_api.route('/client/create/', methods=['POST'])
def add_client():
    '''
        Add client
    '''
    userdata = request.get_json()
    # userdata = request.form
    new_client = ClientsM()
    # print 'userdata', userdata
    res = new_client.create(**userdata)
    return jsonify({"data": res})


@client_api.route('/client/update/<int:id>/', methods=['POST'])
def update_client(id):
    '''
        update client
        id: client id
    '''
    userdata = request.get_json()
    # print userdata
    c_client = ClientsM()
    res = c_client.update(id, **userdata)
    return jsonify({"data": res})


@client_api.route('/client/get/<int:id>/', methods=['GET'])
def get_client_info(id):
    '''
        get client info
        id: client id
    '''
    cl = ClientsM()
    res = cl.get(id)
    app.logger.info('test /client/get/')
    # all_clients = cl.query.all()
    return jsonify({"data": res})


@client_api.route('/client/list/', methods=['GET'])
def list_clients():
    '''
        List all clients
    '''
    u = ClientsM()
    users = u.list_all()
    return jsonify({"data": users})


@client_api.route('/client_vehicle/<int:id>/', methods=['GET'])
def list_client_vehicle(id):
    '''
        list client vehicles
        id: client id
    '''
    vehicle = VehicleM()
    res = vehicle.user_vehicles(id)
    userVehicles = []
    for x in res:
        fuel_rates_his = get_last_fuelrate(x['id'])
        if fuel_rates_his:
            x.update(dict(fuelRateHis=fuel_rates_his))
        else:
            x.update(dict(fuelRateHis=[]))
        period_fuel_rate = get_period_fuelrate(x['id'])
        if period_fuel_rate:
            x.update(dict(fuelRatePeriod=period_fuel_rate))
        else:
            x.update(dict(fuelRatePeriod=[]))
        userVehicles.append(x)
    return jsonify({"data": userVehicles})

