# -*- coding: utf-8 -*-
# @Time    : 19-3-5 上午10:04
import datetime
import json

import requests
from flask import jsonify, request
import time

from api.common_func.utils import compareTime
from api.modules.dispatch import dis_blu


@dis_blu.route('getworklist', methods=['GET', 'POST'])
def get_worklist():
    """获取技师列表"""
    access_key = 'xunjiepf'
    city = request.json.get('city')
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
        params={
            'access_key': access_key,
            'page_size': page_size,
            'city': city
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
            if compareTime(service_date):
                data.append(i)
        #         # print(data)
        # order_no = i["order_no"]
        # res = requests.post(
        #     url='https://banana.xunjiepf.cn/api/extend/orderDetail',
        #     headers={
        #         "Content-Type": "application/json"
        #     },
        #     data=json.dumps({
        #         "access_key": access_key,
        #         "order_no": order_no
        #     })
        # ).json()['data']
        # order_common_info = res['order_common_info']
        # child_list = res['child_list']
        # if len(child_list) > 1:
        #     for i in child_list:
        #         order_dic = {}
        #         service_date = i["service_date"]
        #         if compareTime(service_date):
        #             order_dic['order_no'] = i['order_no']
        #             order_dic['order_id'] = i['parent_id']
        #             order_dic['order_status'] = i['order_status']
        #             order_dic['service_date'] = i['service_date']
        #             order_dic['start_time'] = i['start_time']
        #             order_dic['end_time'] = i['end_time']
        #             order_dic['nick_name'] = order_common_info['nick_name']
        #             order_dic['item_title'] = order_common_info['item_title']
        #             order_dic['address_detail'] = order_common_info['address_detail']
        #             data.append(order_dic)
        # else:
        #     service_date = child_list[0]["service_date"]
        #     order_dic = {}
        #     if compareTime(service_date):
        #         order_dic['order_no'] = child_list[0]['order_no']
        #         order_dic['order_id'] = i["order_id"]
        #         order_dic['order_status'] = child_list[0]['order_status']
        #         order_dic['service_date'] = child_list[0]['service_date']
        #         order_dic['start_time'] = child_list[0]['start_time']
        #         order_dic['end_time'] = child_list[0]['end_time']
        #         order_dic['nick_name'] = order_common_info['nick_name']
        #         order_dic['item_title'] = order_common_info['item_title']
        #         order_dic['address_detail'] = order_common_info['address_detail']
        #         data.append(order_dic)
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


@dis_blu.route('getItemlist', methods=['GET', 'POST'])
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


@dis_blu.route('getOrderDetail', methods=['GET', 'POST'])
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


@dis_blu.route('getMemberList', methods=['GET', 'POST'])
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
