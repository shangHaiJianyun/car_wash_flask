# -*- coding: UTF-8 -*-
"""
share_api.py
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
import os
from wxhelper import *

share_api = Blueprint('share_api', __name__)


@share_api.route('/billboard/get_gid/', methods=['POST'])
def xcx_share_decode():
    '''
        input:
            share_ticket:share_ticket
            s_key: sessionKey
            encryptedData:encryptedData
            iv:iv
        output:
            {u'watermark': {u'timestamp': 1540450935, u'appid': u'wx6327e185ae6c0a46'}, u'openGId': u'tGaLsn4wUI_35zB5KOFeK6f-US1MU'}
    '''
    data = request.get_json()
    encryptedData = data['encryptedData']
    iv = data['iv']
    sessionKey = ['sessionKey']
    res = decode_xcx_data(encryptedData, iv, sessionKey)
    #:  get share group Id
    gid = res['openGId']
    return gid


@share_api.route('/billboard/create/', methods=['POST'])
def create_board():
    '''
        分享后，使用 wx.getShareInfo() 得到 encryptedData 和 iv
        提交 sessionKey ， encryptedData 和 iv 得到 分享的群号 openGId 做为 share_uid
        input:
            {
                    "encryptedData": "encryptedData",
                    "sessionKey": "sessionkdy",
                    "iv": "iv",
                    "client_id": 1,
                    "client_uid": "xcxid1",
                    "client_nick": "client nick",
                    "vehicle_id": 1,
                    "vehicle_name": "my car 1",
                    "fuel_rate": 7.9
            }
        output:
            {
                "client_id": 1,
                "client_nick": "client nick",
                "client_uid": "xcxid1",
                "created_on": "2018-10-26 12:24:30",
                "id": 4,
                "is_active": true,
                "modified_on": "2018-10-26 12:24:30",
                "share_uid": "1212123"
            }
    '''
    data = request.get_json()
    encryptedData = data.pop('encryptedData')
    iv = data.pop('iv')
    sessionKey =data.pop('sessionKey')
    if 'Daniel' in os.getcwd():
        data.update(share_uid = '1212123')
    else:
        res = decode_xcx_data(encryptedData, iv, sessionKey)
        gid = res['openGId']
        data.update(share_uid = gid)
    board = FuelBoardM()
    res = board.create(data)
    return jsonify(res)


@share_api.route('/billboard/get_by_wxdata/', methods=['POST'])
def get_board_dtl_by_ticket():
    '''
        根据 wx.getShareInfo() 得到 encryptedData 和 iv, session_key 获取 排行榜详情
        输入:
            share_ticket:share_ticket
            s_key: sessionKey
            encryptedData:encryptedData
            iv:iv
        返回:
            排行榜详细信息
    '''
    data = request.get_json()
    encryptedData = data['encryptedData']
    iv = data['iv']
    sessionKey = data['sessionKey']
    if 'Daniel' in os.getcwd():
        share_uid = '1212123'
    else:
        res = decode_xcx_data(encryptedData, iv, sessionKey)
        #:  get share group Id
        share_uid = res['openGId']
    board = FuelBoardM()
    res = board.get_dtl(share_uid)
    return jsonify(res)



@share_api.route('/billboard/get_detail/', methods=['POST'])
def get_board_dtl():
    '''
         获取排行榜详情
         输入： 排行榜 群号
         {
             "share_uid": "share_uid"
         }
    '''
    share_uid = request.get_json()['share_uid']
    board = FuelBoardM()
    res = board.get_dtl(share_uid)
    return jsonify(res)


@share_api.route('/billboard/add_fuel_detail/', methods=['POST'])
def add_board_dtl():
    '''
        输入
        {
		"share_uid": "1212123",
		"client_id": 2,
		"client_uid": "xcxid3",
		"client_nick": "user3",
		"vehicle_id": 4,
		"vehicle_name": " 3",
	    "fuel_rate": 7.2
        }
        返回： 排行榜明细
    '''
    data = request.get_json()
    board = FuelBoardM()
    res = board.add_fuel_detail(**data)
    return jsonify(res)


@share_api.route('/billboard/update_fuel_detail/', methods=['POST'])
def update_board_dtl():
    data = request.get_json()
    vehicle_id = data['vehicle_id']
    fuel_rate = data['fuel_rate']
    share_uid = data['share_uid']
    board = FuelBoardM()
    res = board.update_detail(vehicle_id, fuel_rate, share_uid)
    return jsonify(res)    