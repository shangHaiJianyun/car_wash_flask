# -*- coding: utf-8 -*-
# @Time    : 19-3-5 上午10:04
import requests
from flask import jsonify, request
import time

from api.modules.dispatch import dis_blu


@dis_blu.route('getworklist', methods=['GET', 'POST'])
def get_worklist():
    """获取技师列表"""
    access_key = 'xunjiepf'
    results = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getworkerlist",
        params={
            'access_key': access_key
        }
    )
    page_size = results.json()['data']['total_count']
    # print(page_size)

    res = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getworkerlist",
        params={
            'access_key': access_key,
            'page_size': page_size
        }
    )
    # print(res.json())
    return jsonify(res.json()['data']['data'])


@dis_blu.route('getorderlist', methods=['GET', 'POST'])
def get_orderlist():
    """获取订单列表"""
    access_key = 'xunjiepf'
    results = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getorderlist",
        params={
            'access_key': access_key
        }
    )
    page_size = results.json()['data']['total_count']
    res = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getorderlist",
        params={
            'access_key': access_key,
            'page_size': page_size
        }
    )
    return jsonify(res.json()['data']['data'])


@dis_blu.route('dispatchorder', methods=['GET', 'POST'])
def dispatch():
    """派单内容"""
    passwd = 'xunjiepf'
    uid = request.json.get('uid')
    order_ids = request.json.get('order_ids')

    # 获得当前时间时间戳
    now = int(time.time())
    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeStruct = time.localtime(now)
    dispatch_date = time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)
    # print(dispatch_date)

    res = requests.post(
        url='https://banana.xunjiepf.cn/api/dispatch/dispatchorder',
        params={
            'passwd': passwd,
            'uid': uid,
            'order_ids': order_ids,
            'dispatch_date': dispatch_date,
        }
    )

    return jsonify(res)
