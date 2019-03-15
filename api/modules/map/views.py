# -*- coding:utf-8 -*-
import json

from flask import request, jsonify

from api import db
from api.common_func.area import AreaM, AreaRateM
from api.common_func.city_code import level_code
from api.modules.map import map_blu


@map_blu.route('/get_rate', methods=['POST'])
def get_rate():
    # 获取指定坐标后根据中心点坐标确定其所属的区域及价格系数
    # lng:经度  lat:纬度
    lng = float(request.json.get('lng'))
    lat = float(request.json.get('lat'))
    # print(lng, lat)
    # 从数据库中获取所有的坐标数据
    for j in AreaM().get_all():
        # 获取该区域的区域坐标
        i = j.locations
        # 判断指定坐标属于哪个区域
        if (i['lt']['lng'] <= lng <= i['rt']['lng']) and (i['rd']['lat'] <= lat <= i['rt']['lat']):
            rate = AreaRateM().get(j.rate_id)
            # 根据需求返回该坐标所属的价格系数
            level = str(rate['rate_level'])

            rate_level = level_code[str(level)] if level else " "
            data = {
                'rate_name': rate['name'],
                'rate_level': rate_level,
                'area_id': j.id,
                'area_name': j.city_name,
                'city_code': j.city_code
            }
            return jsonify(data)

    return jsonify({'error': 'please input right axis'})


@map_blu.route('/list_area', methods=['GET'])
def list_area():
    result = AreaM().list_all()
    # res = json.dumps(result)
    return jsonify(result)


@map_blu.route('/map_data', methods=['GET', 'POST'])
def map_data():
    # 判断操作的方式 若是修改数据
    if request.method == 'POST':

        id = request.json.get('id')
        level = request.json.get('level')

        try:
            rate_res = AreaRateM().get_obj(level)
            # print(rate_res['id'])
            rate_id = rate_res['id']
            res = AreaM().get(id)
            res.rate_id = rate_id
            db.session.commit()
            # print(res)
            return jsonify({"msg": "modify successfully"})
        except Exception:
            return jsonify({"msg": "please give right data"})
    else:
        # 地图上显示数据
        result = AreaM().list_all()
        return jsonify(result)
