# -*- coding: utf-8 -*-
# @Time    : 18-12-27 下午1:36
# @Author  : dbchen
# @File    : views.py
import requests
from flask import jsonify, request

from api.modules.common import common_blu


@common_blu.route('/get_addr',methods=['POST'])
def get_addr():
    ADDR_KEY='caaeab5bb8c7a2448f1fe7243e752dec'
    # locations的格式为‘0.0000,0.00000’,后期需更改
    locations = request.json.get('locations')
    params = {
        'key':ADDR_KEY,
        'locations': locations,
        'output':'json',
        'coordsys':'gps'
    }
    url = "https://restapi.amap.com/v3/assistant/coordinate/convert"
    res = requests.get(url, params=params)
    return jsonify(res.json())
