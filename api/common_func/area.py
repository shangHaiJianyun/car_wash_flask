# -*- coding: utf-8 -*-
# @Time    : 19-1-2 下午3:29


# 与Area模型相关的数据库操作存储位置
import json
import sys

from api.common_func.CityCode import city_codes
from api.models.models import Area, row2dict, db, Area_rate


class AreaM(object):
    def list_all(self):
        areas = Area.query.all()
        return areas

    def get(self, id):
        res = Area.query.filter(Area.id == id).one_or_none()
        return res

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

    def get_locations(self, name):
        pass

    @staticmethod
    def set_area():
        temp = sys.path[0]
        f = open(temp + '/map.json', encoding='utf-8')
        res = json.load(f)
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

            city_name = i['detail']['addressComponents']['city']
            if city_name:
                city_code = city_codes[city_name] if city_name else ""
            else:
                city_name = ' '
                city_code = ' '
            # 将数据存储在数据库中
            areas = AreaM()
            if count < 1:
                areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
                              sur_count=count, rate_id=3)
            elif count < 2:
                areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
                              sur_count=count, rate_id=2)
            else:
                areas.add_new(city_name=city_name, city_code=city_code, locations=locations, surrounds=surs,
                              sur_count=count, rate_id=1)

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
