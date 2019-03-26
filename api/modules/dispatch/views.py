# -*- coding: utf-8 -*-
# @Time    : 19-3-5 上午10:04
import datetime
import json

import requests
from flask import jsonify, request
import time

from api.modules.dispatch import dis_blu


@dis_blu.route('/getworklist', methods=['GET', 'POST'])
def get_worklist():
    """获取技师列表"""
    access_key = 'xunjiepf'
    city = request.json.get('city')
    date = request.json.get('date', None)
    results = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getworkerlist",
        params={
            'access_key': access_key,
            'city': city
        }
    )
    page_size = results.json()['data']['total_count']
    # print(page_size)

    res = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getworkerlist",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({
            'access_key': access_key,
            'page_size': page_size,
            'city': city,
            "date": date
        })
    )
    # print(res.json())
    return jsonify(res.json()['data']['data'])


@dis_blu.route('/getorderlist', methods=['GET', 'POST'])
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
    if request.method == 'POST':
        order_status = request.json.get('order_status')
        start_service_date = request.json.get('start_service_date')
        end_service_date = request.json.get('end_service_date')
        res = requests.post(
            url="https://banana.xunjiepf.cn/api/extend/getorderlist",
            headers={
                "Content-Type": "application/json"
            },
            data=json.dumps({
                'access_key': access_key,
                'page_size': page_size,
                'order_status': order_status,
                'start_service_date': start_service_date,
                'end_service_date': end_service_date
            })
        )
    else:
        res = requests.post(
            url="https://banana.xunjiepf.cn/api/extend/getorderlist",
            params={
                'access_key': access_key,
                'page_size': page_size,
            }
        )
    result = res.json()['data']['data']
    # return jsonify(res.json()['data']['data'])
    return jsonify(result)


@dis_blu.route('/dispatchorder', methods=['GET', 'POST'])
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


@dis_blu.route('/updateOrderStatus', methods=['GET', 'POST'])
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


@dis_blu.route('/getItemlist', methods=['GET', 'POST'])
def getItemlist():
    """获取项目列表"""
    access_key = 'xunjiepf'
    city = request.json.get("city")
    params = {
        "access_key": access_key,
        "city": city
    }
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/getItemlist',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(params)
    )
    return jsonify(res.json()['data'])


@dis_blu.route('/getOrderDetail', methods=['GET', 'POST'])
def getOrderDetail():
    """获取订单详情"""
    access_key = 'xunjiepf'
    order_no = request.json.get("order_no")
    params = {
        "access_key": access_key,
        "order_no": order_no
    }
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/orderDetail',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(params)
    )
    return jsonify(res.json()['data'])


@dis_blu.route('/getMemberList', methods=['GET', 'POST'])
def getMemberList():
    """获取用户列表"""
    access_key = 'xunjiepf'
    city = request.json.get('city')

    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/getMemberList',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({
            'access_key': access_key,
            'city': city
        })
    )
    page_size = res.json()['data']['total_count']
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/getMemberList',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({
            'access_key': access_key,
            'page_size': page_size,
            'city': city
        })
    )
    return jsonify(res.json()['data']['data'])


@dis_blu.route('/getParentOrderList', methods=['GET', 'POST'])
def getParentOrderList():
    """获取父订单信息"""
    access_key = 'xunjiepf'
    city = request.json.get('city')
    start_date = request.json.get('start_date', '')
    end_date = request.json.get('end_date', '')
    order_status = request.json.get('order_status', 1)
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/getParentOrderList',
        params={
            'access_key': access_key,
            'city': city
        })
    page_size = res.json()['data']['total_count']
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/getParentOrderList',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({
            'access_key': access_key,
            'page_size': page_size,
            'city': city,
            'start_date': start_date,
            'end_date': end_date,
            'order_status': order_status
        })
    )
    return jsonify(res.json()['data']['data'])
