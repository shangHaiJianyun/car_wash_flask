# -*- coding: utf-8 -*-
# @Time    : 19-3-5 上午10:04
import json

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
    # uid = request.json.get('uid')
    # order_ids = request.json.get('order_ids')
    # dispatch_date = request.json.get('dispatch_date')
    # print(order_ids, uid)
    # start_time = request.json.get("start_time")
    # end_time = request.json.get("end_time")
    # print(start_time,end_time)
    data = request.json.get("data")

    # # 获得当前时间时间戳
    # now = int(time.time())
    # # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    # timeStruct = time.localtime(now)
    # dispatch_date = time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)
    params = {
        "passwd": passwd,
        # "uid": uid,
        # "order_ids": order_ids,
        # # "dispatch_date": dispatch_date
        # "start_time": start_time,
        # "end_time": end_time
        "data": data

    }
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/dispatch/dispatchorder',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(params)
    )
    # print(res.json())
    return jsonify(res.json())


@dis_blu.route('updateOrderStatus', methods=['GET', 'POST'])
def updateStatus():
    """更新订单状态"""
    access_key = 'xunjiepf'
    order_ids = request.json.get("order_ids")
    order_status = request.json.get("order_status")
    print(order_ids, type(order_ids))
    print(order_status, type(order_status))
    params = {
        "access_key": access_key,
        "order_ids": order_ids,
        "order_status": order_status
    }
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/updateOrderStatus',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(params)
    )
    # print(res.json())
    return jsonify(res.json())
