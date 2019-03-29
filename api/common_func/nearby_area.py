# -*- coding: utf-8 -*-
# @Time    : 19-1-11 上午9:47
# import datetime
# import time
#
#
# def compareTime(service_date):
#     time_array = time.strptime(service_date, "%Y-%m-%d")
#     service_time = time.mktime(time_array)
#     acquire = datetime.date.today() + datetime.timedelta(days=2)
#     tomorrow_end_time = int(time.mktime(time.strptime(str(acquire), '%Y-%m-%d'))) - 1
#     today = datetime.date.today()
#     today_time = int(time.mktime(today.timetuple()))
#
#     # print(service_time, now)
#     if today_time <= service_time < tomorrow_end_time:
#         return True
#     else:
#         return False
import json
from math import cos, sin, sqrt, pi, tan, atan2

import requests

from api import NearbyArea
from api.common_func.area import AreaM, NearbyM


class GetLocation(object):
    """
    大地坐标系资料WGS - 84
    长半径a = 6378137
    短半径b = 6356752.3142
    扁率f = 1 / 298.2572236
    """
    # 长半径a = 6378137
    _a = 6378137
    # 短半径b = 6356752.3142
    _b = 6356752.3142
    # 扁率f = 1 / 298.2572236
    _f = 1 / 298.2572236

    def __init__(self, lon, lat, brng, dis):
        self.lon = lon
        self.lat = lat
        self.brng = brng
        self.dis = dis

    def rad(self, d):
        # 将度换成弧度
        return d * pi / 180.0

    def deg(self, x):
        # 将弧度换成度
        return x * 180 / pi

    def calculate_loc(self):
        alpha1 = self.rad(self.brng)
        sinAlpha1 = sin(alpha1)
        cosAlpha1 = cos(alpha1)

        tanU1 = (1 - self._f) * tan(self.rad(self.lat))
        cosU1 = 1 / sqrt((1 + tanU1 * tanU1))
        sinU1 = tanU1 * cosU1
        sigma1 = atan2(tanU1, cosAlpha1)
        sinAlpha = cosU1 * sinAlpha1
        cosSqAlpha = 1 - sinAlpha * sinAlpha
        uSq = cosSqAlpha * (self._a * self._a - self._b * self._b) / (self._b * self._b)
        A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
        B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))

        cos2SigmaM = 0
        sinSigma = 0
        cosSigma = 0
        sigma = self.dis / (self._b * A)
        sigmaP = 2 * pi
        while abs(sigma - sigmaP) > 1e-12:
            cos2SigmaM = cos(2 * sigma1 + sigma)
            sinSigma = sin(sigma)
            cosSigma = cos(sigma)
            deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)
                                                               - B / 6 * cos2SigmaM * (-3 + 4 * sinSigma * sinSigma) * (
                                                                       -3 + 4 * cos2SigmaM * cos2SigmaM)))
            sigmaP = sigma
            sigma = self.dis / (self._b * A) + deltaSigma

        tmp = sinU1 * sinSigma - cosU1 * cosSigma * cosAlpha1
        lat2 = atan2(sinU1 * cosSigma + cosU1 * sinSigma * cosAlpha1,
                     (1 - self._f) * sqrt(sinAlpha * sinAlpha + tmp * tmp))
        amb = atan2(sinSigma * sinAlpha1, cosU1 * cosSigma - sinU1 * sinSigma * cosAlpha1)
        C = self._f / 16 * cosSqAlpha * (4 + self._f * (4 - 3 * cosSqAlpha))
        L = amb - (1 - C) * self._f * sinAlpha * (
                sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)))
        # revAz = atan2(sinAlpha, -tmp)
        # print(revAz)

        return self.lon + self.deg(L), self.deg(lat2)


def get_ride(origin, destination):
    """
    根据两地的经纬度获取骑行路线及骑行时间
    {'data': {'destination': '121.62486,29.92326568537871',
        'origin': '121.62486, 29.87816',
        'paths': [{'distance': 7986, 'duration': 1917}]}'errcode': 0, 'errdetail': None, 'errmsg': 'OK', 'ext': None}

    :return:
    """
    res = requests.get(
        url="https://restapi.amap.com/v4/direction/bicycling",
        params={
            "origin": origin,
            "destination": destination,
            "key": "1bf70fc7ddc08a270db490535b1b5112"
        }
    ).json()
    dis = res['data']['paths'][0]['distance']
    time = res['data']['paths'][0]['duration']
    return dis, time


def set_nearby():
    """
    nearby:
    {
    ul:左上  -45° 3.14*5000m
    uu:上   0°  5000m
    ur:右上  45° 3.14*5000m
    ll:左  -90° 5000m
    rr:右  90° 5000m
    dl:左下  -135° 3.14*5000m
    dd:下  180° 5000m
    dr:右下 135° 3.14*5000m
    }

    uu,ul,ur...:{
        "area_id":"区域id",
        "area_cen":"区域中心点",
        "area_name":"区域名称",
        "distance":"距离",
        "ridding_time":"骑行时间",

    }
    :return:
    """
    _dis = 5000
    _long = 7070
    areas = AreaM().get_area("上海市")
    for i in areas:
        # 区域id
        id = i.id
        lng = i.locations['cen']['lng']
        lat = i.locations['cen']['lat']

        # ul
        ul = {}
        lng1, lat1 = GetLocation(lng, lat, -45, _long).calculate_loc()
        origin = '{0}, {1}'.format(lng, lat)
        destination1 = '{0}, {1}'.format(lng1, lat1)
        # ul = generate_u(ul, areas, lng1, lat1, origin, destination1)
        # print(ul)
        dis1, ridding_time1 = get_ride(origin, destination1)
        for n in areas:
            # 获取该区域的区域坐标
            j = n.locations
            # 判断指定坐标属于哪个区域
            if (j['lt']['lng'] <= lng1 <= j['rt']['lng']) and (j['rd']['lat'] <= lat1 <= j['rt']['lat']):
                area_id = n.id
                area_name = n.area_description
                ul['area_id'] = area_id
                ul['area_cen'] = j['cen']
                ul['area_name'] = area_name
                ul['distance'] = dis1
                ul['ridding_time'] = ridding_time1
                # print(ul)

        # uu
        uu = {}
        lng2, lat2 = GetLocation(lng, lat, 0, _dis).calculate_loc()
        destination2 = '{0}, {1}'.format(lng2, lat2)
        dis2, ridding_time2 = get_ride(origin, destination2)
        for n in areas:
            # 获取该区域的区域坐标
            j = n.locations
            # 判断指定坐标属于哪个区域
            if (j['lt']['lng'] <= lng2 <= j['rt']['lng']) and (j['rd']['lat'] <= lat2 <= j['rt']['lat']):
                area_id = n.id
                area_name = n.area_description
                uu['area_id'] = area_id
                uu['area_cen'] = j['cen']
                uu['area_name'] = area_name
                uu['distance'] = dis2
                uu['ridding_time'] = ridding_time2

        # ur
        ur = {}
        lng3, lat3 = GetLocation(lng, lat, 45, _long).calculate_loc()
        destination3 = '{0}, {1}'.format(lng3, lat3)
        dis3, ridding_time3 = get_ride(origin, destination3)
        for n in areas:
            # 获取该区域的区域坐标
            j = n.locations
            # 判断指定坐标属于哪个区域
            if (j['lt']['lng'] <= lng3 <= j['rt']['lng']) and (j['rd']['lat'] <= lat3 <= j['rt']['lat']):
                area_id = n.id
                area_name = n.area_description
                ur['area_id'] = area_id
                ur['area_cen'] = j['cen']
                ur['area_name'] = area_name
                ur['distance'] = dis3
                ur['ridding_time'] = ridding_time3

        # ll
        ll = {}
        lng4, lat4 = GetLocation(lng, lat, -90, _dis).calculate_loc()
        destination4 = '{0}, {1}'.format(lng4, lat4)
        dis4, ridding_time4 = get_ride(origin, destination4)
        for n in areas:
            # 获取该区域的区域坐标
            j = n.locations
            # 判断指定坐标属于哪个区域
            if (j['lt']['lng'] <= lng4 <= j['rt']['lng']) and (j['rd']['lat'] <= lat4 <= j['rt']['lat']):
                area_id = n.id
                area_name = n.area_description
                ll['area_id'] = area_id
                ll['area_cen'] = j['cen']
                ll['area_name'] = area_name
                ll['distance'] = dis4
                ll['ridding_time'] = ridding_time4

        # rr
        rr = {}
        lng5, lat5 = GetLocation(lng, lat, 90, _dis).calculate_loc()
        destination5 = '{0}, {1}'.format(lng5, lat5)
        dis5, ridding_time5 = get_ride(origin, destination5)
        for n in areas:
            # 获取该区域的区域坐标
            j = n.locations
            # 判断指定坐标属于哪个区域
            if (j['lt']['lng'] <= lng5 <= j['rt']['lng']) and (j['rd']['lat'] <= lat5 <= j['rt']['lat']):
                area_id = n.id
                area_name = n.area_description
                rr['area_id'] = area_id
                rr['area_cen'] = j['cen']
                rr['area_name'] = area_name
                rr['distance'] = dis5
                rr['ridding_time'] = ridding_time5

        # dl
        dl = {}
        lng6, lat6 = GetLocation(lng, lat, -135, _long).calculate_loc()
        destination6 = '{0}, {1}'.format(lng6, lat6)
        dis6, ridding_time6 = get_ride(origin, destination6)
        for n in areas:
            # 获取该区域的区域坐标
            j = n.locations
            # 判断指定坐标属于哪个区域
            if (j['lt']['lng'] <= lng6 <= j['rt']['lng']) and (j['rd']['lat'] <= lat6 <= j['rt']['lat']):
                area_id = n.id
                area_name = n.area_description
                dl['area_id'] = area_id
                dl['area_cen'] = j['cen']
                dl['area_name'] = area_name
                dl['distance'] = dis6
                dl['ridding_time'] = ridding_time6

        # dd
        dd = {}
        lng7, lat7 = GetLocation(lng, lat, 180, _dis).calculate_loc()
        destination7 = '{0}, {1}'.format(lng7, lat7)
        dis7, ridding_time7 = get_ride(origin, destination7)
        for n in areas:
            # 获取该区域的区域坐标
            j = n.locations
            # 判断指定坐标属于哪个区域
            if (j['lt']['lng'] <= lng7 <= j['rt']['lng']) and (j['rd']['lat'] <= lat7 <= j['rt']['lat']):
                area_id = n.id
                area_name = n.area_description
                dd['area_id'] = area_id
                dd['area_cen'] = j['cen']
                dd['area_name'] = area_name
                dd['distance'] = dis7
                dd['ridding_time'] = ridding_time7

        # dr
        dr = {}
        lng8, lat8 = GetLocation(lng, lat, 135, _long).calculate_loc()
        destination8 = '{0}, {1}'.format(lng8, lat8)
        dis8, ridding_time8 = get_ride(origin, destination8)
        for n in areas:
            # 获取该区域的区域坐标
            j = n.locations
            # 判断指定坐标属于哪个区域
            if (j['lt']['lng'] <= lng8 <= j['rt']['lng']) and (j['rd']['lat'] <= lat8 <= j['rt']['lat']):
                area_id = n.id
                area_name = n.area_description
                dr['area_id'] = area_id
                dr['area_cen'] = j['cen']
                dr['area_name'] = area_name
                dr['distance'] = dis8
                dr['ridding_time'] = ridding_time8
        nearby = {
            "ul": ul,
            "uu": uu,
            "ur": ur,
            "ll": ll,
            "rr": rr,
            "dl": dl,
            "dd": dd,
            "dr": dr
        }
        NearbyM().add_new(area_id=id, nearby=nearby)
        # return nearby
