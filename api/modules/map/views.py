# -*- coding:utf-8 -*-

from flask import request, jsonify

from api.models.models import Area, Area_rate
from api.modules.map import map_blu


@map_blu.route('/get_rate', methods=['POST'])
def get_rate():
    # 获取指定坐标后根据中心点坐标确定其所属的区域及价格系数
    # lng:经度  lat:纬度
    location = request.json.get('location')
    lng = location['lng']
    lat = location['lat']
    # print(locations)
    areas = Area.query.all()
    # area_axis = request.json.get('area_axis')
    for i in areas:
        if (i['lt']['lng'] <= lng <= i['rt']['lng']) and (i['lt']['lat'] <= lat <= i['lt']['lat']):
            area = Area.query.filter_by()
            rate = Area_rate.query.filter_by(id=area.rate_id)
            return jsonify(rate_level=rate.rate_level)
