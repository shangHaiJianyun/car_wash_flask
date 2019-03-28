# -*- coding: utf-8 -*-
# @Time    : 19-1-2 下午3:29


# 与Area模型相关的数据库操作存储位置
import json
import sys

from api.common_func.city_code import city_codes, level_code
from api.common_func.utils import GetLocation, get_ride
from api.models.models import Area, row2dict, db, Area_rate, NearbyArea


class AreaM(object):
    def get_all(self):
        areas = Area.query.all()
        return areas

    def list_all(self):
        areas = Area.query.all()
        json_list = []
        for i in areas:
            json_dict = {}
            json_dict["area_id"] = i.id
            # json_dict["rate_id"] = i.rate_id
            json_dict["cen_loc"] = i.locations['cen']
            level = AreaRateM().get(i.rate_id)['rate_level']
            # print(level)
            sur = i.surrounds['surrounds'][0]['title'] if i.surrounds['surrounds'] else " "
            # print(sur)
            rate_level = level_code[str(level)] if level else " "
            json_dict["level"] = level
            json_dict["surrounds"] = sur
            json_dict["area_rate"] = rate_level
            json_dict["business"] = i.business
            json_dict["address"] = i.address
            json_list.append(json_dict)

        return json_list

    def get(self, id):
        res = Area.query.get(id)

        if res:
            return res
        else:
            return None

    def add_new(self, **args):
        new_co = Area(**args)
        db.session.add(new_co)
        db.session.commit()
        return self.get(new_co.id)

    def update(self, id, param):
        # print id, param
        new_co = Area.query.filter(Area.id == id).update(param)
        db.session.commit()
        return self.get(new_co.id)

    def delete(self, id):
        tmp = Area.query.filter(Area.id == id)
        db.session.delete(tmp.one())
        db.session.commit()
        return 'success'

    def get_area(self, name):
        res = Area.query.filter(Area.city_name == name).one_or_none()
        return res

    @staticmethod
    def set_area():
        temp = sys.path[0]
        with open(temp + '/mapAll.json', encoding='utf-8') as f:
            res = json.load(f)
            # print(res)
            f.close()
        for i in res:
            # lng:经度,lat:纬度
            # 区域坐标：
            locations = {
                'cen': i['cen'],
                'lt': i['lt'],
                'ld': i['ld'],
                'rt': i['rt'],
                'rd': i['rd']
            }
            # 周边建筑群：
            surs = {
                'surrounds': i['detail']['surroundingPois']
            }
            count = len(surs['surrounds'])
            business = i['detail']['business']
            city_name = i['detail']['addressComponents']['city']
            address = i['detail']['address']
            if city_name:
                city_code = city_codes[city_name] if city_name else ""
            else:
                city_name = ' '
                city_code = ' '
            # 将数据存储在数据库中
            areas = AreaM()
            if count < 1:
                areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
                              sur_count=count, business=business, address=address, rate_id=2)
            else:
                areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
                              sur_count=count, address=address, business=business, rate_id=1)

        return 'set data successfully!'


class AreaRateM(object):
    def list_all(self):
        pass

    def get(self, id):
        res = Area_rate.query.filter(Area_rate.id == id).one_or_none()
        return row2dict(res)

    def add_new(self, **args):
        new_co = Area_rate(**args)
        db.session.add(new_co)
        db.session.commit()
        return self.get(new_co.id)

    def get_obj(self, level):
        res = Area_rate.query.filter(Area_rate.rate_level == level).one_or_none()
        return row2dict(res)


class NearbyM(object):
    def list_all(self):
        nearby = NearbyArea.query.all()
        return nearby

    def get(self, area_id):
        res = NearbyArea.query.filter(NearbyArea.area_id == area_id).one_or_none()
        return row2dict(res)

    def add_new(self, **args):
        new_co = NearbyArea(**args)
        db.session.add(new_co)
        db.session.commit()
        return self.get(new_co.id)

    @staticmethod
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
            lng = i.locations['cen']['lng']
            lat = i.locations['cen']['lat']
            lng1, lat1 = GetLocation(lng, lat, -45, _dis)
            origin = '{0}, {1}'.format(lng, lat)
            destination = '{0}, {1}'.format(lng1, lat1)
            dis, ridding_time = get_ride(origin, destination)
            pass
