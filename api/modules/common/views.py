# -*- coding: utf-8 -*-
# @Time    : 18-12-27 下午1:36
# @Author  : dbchen
# @File    : views.py
import requests
from flask import jsonify, request

from api.models.models import Area, db
from api.modules.common import common_blu
import json


# @common_blu.route('/get_addr',methods=['POST'])
# def get_addr():
#     ADDR_KEY='caaeab5bb8c7a2448f1fe7243e752dec'
#     # locations的格式为‘0.0000,0.00000’,后期需更改
#     locations = request.json.get('locations')
#     params = {
#         'key':ADDR_KEY,
#         'locations': locations,
#         'output':'json',
#         'coordsys':'gps'
#     }
#     url = "https://restapi.amap.com/v3/assistant/coordinate/convert"
#     res = requests.get(url, params=params)
#

@common_blu.route('/set_area')
def set_area():
    f = open('../mapIndex.json', encoding='utf-8')
    res = json.load(f)
    for i in res:
        # lng:经度,lat:纬度
        data = i
        # 将数据存储在数据库中
        area = Area()
        area.locations = data
        area.city_name = 'shanghai'
        area.city_code = '200000'
        db.session.commit()

    return 'set data successfully!'
