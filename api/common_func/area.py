# -*- coding: utf-8 -*-
# @Time    : 19-1-2 下午3:29


# 与Area模型相关的数据库操作存储位置
from api.models.models import Area, row2dict, db, Area_rate


class AreaM(object):
    def list_all(self, name):
        areas = Area.query.all()
        res = []
        for d in areas:
            res.append(row2dict(d))
        return res

    def get(self, id):
        res = Area.query.filter(Area.id == id).one_or_none()
        return row2dict(res)

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


class AreaRateM(object):
    def list_all(self):
        pass

    def get(self,id):
        pass

    def add_new(self, **args):
        new_co = Area_rate(**args)
        db.session.add(new_co)
        db.session.commit()
        return self.get(new_co.id)