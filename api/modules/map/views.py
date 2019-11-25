# -*- coding:utf-8 -*-
import json

from flask import request, jsonify

from api import db, row2dict
from api.models.models import SearchRecord
from api.common_func.area import AreaM, AreaRateM, NearbyM, gen_loc
from api.common_func.city_code import level_code
from api.common_func.nearby_area import set_nearby
from api.common_func.tx_to_bd import convert
from api.modules.map import map_blu
import numpy as np

from api.modules.scheduler import SchJobs, SchWorkers


@map_blu.route('/get_rate', methods=['POST'])
def get_rate():
    """
        根据经纬度获取该区域的价格系数
        小程序后台使用
    :return:
        data = {
                    'rate_name': rate['name'],
                    'rate_level': rate_level,
                    'area_id': j.id,
                    'city': j.city_name,
                    'city_code': j.city_code
                }
    """
    # 获取指定坐标后根据中心点坐标确定其所属的区域及价格系数
    # lng:经度  lat:纬度
    tx_lng = float(request.json.get('lng'))
    tx_lat = float(request.json.get('lat'))
    lat, lng = convert(tx_lat, tx_lng)

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
                'city': j.city_name,
                'city_code': j.city_code
            }
            return jsonify(data if j.active else None)

    return jsonify(None)


@map_blu.route('/list_area', methods=['GET'])
def list_area():
    """
        列出区域信息
    :return:
    """
    result = AreaM().list_all()
    # res = json.dumps(result)
    return jsonify(result)


@map_blu.route('/map_data', methods=['GET', 'POST'])
def map_data():
    """
        GET:列出区域地图信息
        POST:更改区域系数
    :return:
    """
    # 判断操作的方式 若是修改数据
    if request.method == 'POST':

        id = request.json.get('id')
        level = request.json.get('level')

        try:
            rate_res = AreaRateM().get_obj(level)
            # print(rate_res['id'])
            rate_id = rate_res['id']
            res = AreaM().get_obj(id)
            res.rate_id = rate_id
            db.session.commit()
            # print(res)
            return jsonify(dict(area_rate=level_code[str(level)] if level else " "))
        except Exception as e:
            return jsonify(dict(msg=e))
    else:
        # 地图上显示数据
        result = AreaM().list_all()
        return jsonify(result)


@map_blu.route('/change_status', methods=['POST'])
def change_status():
    """
        更改区域开通状态
    :return:
    """
    area_id = request.json.get('area_id')
    active = request.json.get('active')
    try:
        res = AreaM().get_obj(area_id)
        res.active = active
        db.session.commit()
        return jsonify(dict(AreaM().get(area_id)))
    except Exception as e:
        return jsonify(dict(erro=e))


@map_blu.route('/get_w_j_count', methods=['POST'])
def get_w_j_count():
    """
        获取该区域的技师和订单数量
    :return:
    """
    region_id = request.json.get('region_id')
    try:
        j_count = SchJobs('上海市').get_j_count_by_region(region_id)
        w_count = SchWorkers('上海市').get_w_count_by_region(region_id)
        active = AreaM().get(region_id)['active']
        return jsonify(dict(region_id=region_id, j_count=j_count, w_count=w_count, active=active))
    except Exception as e:
        return jsonify(dict(erro=e))


@map_blu.route('/get_active_area', methods=['GET'])
def get_active_area():
    """
        获取已激活的区域
    :return:
    """
    areas = AreaM().get_active_obj()
    area = []
    if areas:
        for i in areas:
            area.append(row2dict(i))
        return jsonify(dict(active_area=area))
    else:
        return jsonify(dict(active_area=[]))


@map_blu.route('/judge_active_area', methods=['POST'])
def judge_active_area():
    """
        判断该地址所属区域是否已开通服务
    :return:
    """
    lng = float(request.json.get('lng'))
    lat = float(request.json.get('lat'))
    unionid = request.json.get('unionid')
    openid = request.json.get('openid')
    address = request.json.get('address')
    location = json.dumps(dict(lng=lng, lat=lat))
    if openid:
        record = SearchRecord(openid=openid, unionid=unionid, locations=location, address=address)
        record.save()
    for j in AreaM().get_all():
        i = j.locations
        if (i['lt']['lng'] <= lng <= i['rt']['lng']) and (i['rd']['lat'] <= lat <= i['rt']['lat']):
            active = j.active
            return jsonify(dict(active=active))
    return jsonify(dict(active=False))


@map_blu.route('/activate_region', methods=['POST'])
def activate_region():
    """
        按照规则激活技师活动区域附近的区域
    :return:
    """
    lng = float(request.json.get('lng'))
    lat = float(request.json.get('lat'))
    for j in AreaM().get_all():
        i = j.locations
        if (i['lt']['lng'] <= lng <= i['rt']['lng']) and (i['rd']['lat'] <= lat <= i['rt']['lat']):
            area_id = j.id
            nearby_info = NearbyM().get_nearby(area_id)
            if nearby_info:
                dd_region_id = nearby_info['dd']['area_id'] if nearby_info['dd'] else " "
                dl_region_id = nearby_info['dl']['area_id'] if nearby_info['dl'] else " "
                dr_region_id = nearby_info['dr']['area_id'] if nearby_info['dr'] else " "
                ll_region_id = nearby_info['ll']['area_id'] if nearby_info['ll'] else " "
                rr_region_id = nearby_info['rr']['area_id'] if nearby_info['rr'] else " "
                ul_region_id = nearby_info['ul']['area_id'] if nearby_info['ul'] else " "
                ur_region_id = nearby_info['ur']['area_id'] if nearby_info['ur'] else " "
                uu_region_id = nearby_info['uu']['area_id'] if nearby_info['uu'] else " "
                dd = AreaM().get_obj(dd_region_id)
                dd.active = 1
                dl = AreaM().get_obj(dl_region_id)
                dl.active = 1
                dr = AreaM().get_obj(dr_region_id)
                dr.active = 1
                ll = AreaM().get_obj(ll_region_id)
                ll.active = 1
                rr = AreaM().get_obj(rr_region_id)
                rr.active = 1
                ul = AreaM().get_obj(ul_region_id)
                ul.active = 1
                ur = AreaM().get_obj(ur_region_id)
                ur.active = 1
                uu = AreaM().get_obj(uu_region_id)
                uu.active = 1
                j.active = 1
                db.session.commit()
                return jsonify(dict(erro='activate success'))
    return jsonify(dict(erro='invalid area'))


@map_blu.route('/rate', methods=['GET', 'POST'])
def return_rate():
    """
        根据区域id获取系数
    :return:
    """
    area_id = request.json.get('area_id')
    try:
        area = AreaM().get(area_id)
        res = AreaRateM().get(area.rate_id)
        area_rate = level_code[str(res['rate_level'])] if res['rate_level'] else " "
    except Exception:
        return jsonify({'erro': 'wrong area_id'})
    return jsonify({'area_rate': area_rate})


@map_blu.route('get_nearby', methods=['GET', 'POST'])
def get_nearby():
    """
        获取某一区域id或者是中心点坐标 返回附近8个区域的信息
    """
    try:
        area_id = request.json.get('area_id')
        res = NearbyM().get_nearby(area_id)['nearby']
    except Exception as e:
        raise e
    return jsonify(res)


@map_blu.route('cluster_address', methods=['GET', 'POST'])
def cluster_address():
    from api.common_func.cluster_address import cluster
    try:
        loc = request.json.get('loc')
        loc_data = np.array(loc)
        labels, lat_label = cluster(loc_data)
        print(labels)
        print("==========")
        print(lat_label)
        data = dict(labels=labels.tolist(), lat_label=lat_label.tolist())
    except Exception as e:
        return {'erro': e}

    return jsonify({'data': data})


@map_blu.route('test_gen', methods=['GET', 'POST'])
def gen_location():
    id = request.args.get("id")
    # lat, lng = gen_loc(id)
    # return jsonify(dict(lat=lat, lng=lng))
    loc, loc_name = gen_loc(id)
    return jsonify(dict(loc=loc, loc_name=loc_name))
