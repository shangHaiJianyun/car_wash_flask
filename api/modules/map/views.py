# -*- coding:utf-8 -*-

from flask import request

from api.modules.map import map_blu


@map_blu.route('/get_msg', methods=['POST'])
def get_msg():
    # lng:经度  lat:纬度
    locations = request.json.get('locations')
    print(locations)
    area_axis = request.json.get('area_axis')
    pass
