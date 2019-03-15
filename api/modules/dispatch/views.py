# -*- coding: utf-8 -*-
# @Time    : 19-3-5 上午10:04
import datetime
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
    result = res.json()['data']['data']
    data = []
    for i in result:
        service_date = i['service_date']
        # print(service_date)
        if service_date:
            timeArray = time.strptime(service_date, "%Y-%m-%d")
            service_time = time.mktime(timeArray)
            acquire = datetime.date.today() + datetime.timedelta(days=2)
            tomorrow_end_time = int(time.mktime(time.strptime(str(acquire), '%Y-%m-%d'))) - 1
            now = int(time.time())

            # print(service_time, now)
            if now < service_time < tomorrow_end_time:
                data.append(i)
                # print(data)
    # print(res.json())
    # return jsonify(res.json()['data']['data'])
    return jsonify(data)


@dis_blu.route('dispatchorder', methods=['GET', 'POST'])
def dispatch():
    """派单内容"""
    passwd = 'xunjiepf'
    # 获取传输参数
    data = request.json.get("data")

    # # 获得当前时间时间戳
    # now = int(time.time())
    # # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    # timeStruct = time.localtime(int(time.time()))
    dispatch_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    # 获取服务时间的时间戳
    for i in data[0]['orders']:
        service_date = i['start_time']
        timeArray = time.strptime(service_date, "%Y-%m-%d %H:%M")

        # timeD = 86400.0  # 隔天的时间戳差值
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow_start_time = int(time.mktime(tomorrow.timetuple()))

        if time.mktime(timeArray) < tomorrow_start_time:
            deadline = 15
        else:
            deadline = 60

        # print(deadline)
        params = {
            "passwd": passwd,
            "dispatch_info": {"data": data},
            "dispatch_date": dispatch_date,
            "deadline": deadline
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
    # print(order_ids, type(order_ids))
    # print(order_status, type(order_status))
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
