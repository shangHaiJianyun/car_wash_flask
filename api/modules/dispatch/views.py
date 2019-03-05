# -*- coding: utf-8 -*-
# @Time    : 19-3-5 上午10:04
import requests
from flask import jsonify

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
    return jsonify(res.json()['data'])


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
    return jsonify(res.json()['data'])

@dis_blu.route('dispatchorder', methods=['GET', 'POST'])
def dispatch():
    """派单内容"""
    pass


