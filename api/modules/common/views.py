# -*- coding: utf-8 -*-
# @Time    : 18-12-27 下午1:36


# import sys
#
# import requests
# from flask import jsonify, request
#
# from api.common_func.CityCode import city_codes
# from api.common_func.area import AreaM
# from api.models.models import Area, db
# from api.modules.common import common_blu
# import json
#
#
# @common_blu.route('/set_area')
# def set_area():
#     temp = sys.path[0]
#     f = open(temp + '/map.json', encoding='utf-8')
#     res = json.load(f)
#     for i in res:
#         # lng:经度,lat:纬度
#         # 区域坐标：
#         locations = {
#             'cen': i['cen'],
#             'lt': i['lt'],
#             'ld': i['ld'],
#             'rt': i['rt'],
#             'rd': i['rd']
#         }
#         # 周边建筑群：
#         surs = {
#             'surrounds': i['detail']['surroundingPois']
#         }
#         count = len(surs['surrounds'])
#
#         city_name = i['detail']['addressComponents']['city']
#         if city_name:
#             city_code = city_codes[city_name] if city_name else ""
#         else:
#             city_name = ' '
#             city_code = ' '
#         # 将数据存储在数据库中
#         areas = AreaM()
#         if count < 1:
#             areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
#                           sur_count=count, rate_id=3)
#         elif count < 2:
#             areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
#                           sur_count=count, rate_id=2)
#         else:
#             areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
#                           sur_count=count, rate_id=1)
#
#     return 'set data successfully!'
