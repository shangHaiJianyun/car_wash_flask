# -*- coding: UTF-8 -*-

"""
user_client.py
- manage users
"""
# import json
# from flask import Blueprint, jsonify, request
from model.models import db, row2dict, Clients, User, UserCompany, Role, UserRoles
from vehicle_fuel import *

class ClientsM(object):
    def list_all(self):
        user = Clients.query.all()
        res = []
        for d in user:
            # print type(d)
            res.append(row2dict(d))
        return res

    def get(self, id):
        res = Clients.query.filter(Clients.id == id).one_or_none()
        return row2dict(res)


    def create(self, **args):
        new_client = Clients(**args)
        db.session.add(new_client)
        db.session.commit()
        return self.get(new_client.id)

    def update(self, id, **param):
        # print id, param
        c_client = Clients.query.filter(Clients.id == id).update(param)
        db.session.commit()
        return self.get(c_client)

    def delete(self, id):
        tmp = Clients.query.filter(Clients.id == id)
        db.session.delete(tmp.one())
        db.session.commit()
        return 'success'

    def add_client_sys(self, id, **args):
        c_sys = ClientSystem.query.filter(ClientSystem.user_id == id).all()
        if c_sys:
            c_sys.update(**args)
            db.session.commit()
            return dict(status="success")
        else:
            new_sys = ClientSystem(**args)
            db.session.add(new_sys)
            db.session.commit()
            return dict(status="success")

    def get_client_by_xcxid(self, xcxId):
        res = Clients.query.filter(Clients.xcxId == xcxId).one_or_none()
        return row2dict(res)


class FuelBoardM(object):
    '''
        油耗排名
    '''
    def list_all(self):
        bs = Fuel_Billboard.query.all()
        return [row2dict(x) for x in bs]

    def get(self, uid):
        res = Fuel_Billboard.query.filter(Fuel_Billboard.share_uid == uid).one_or_none()
        return row2dict(res)


    def create(self, data):
        share_info = dict(
            share_uid = data['share_uid'],
            client_id=data['client_id'],
            client_uid=data['client_uid'],
            client_nick = data['client_nick']
        )
        q = Fuel_Billboard.query.filter(Fuel_Billboard.share_uid == share_info['share_uid']).one_or_none()
        if q:
            return self.get(q.id)
        new_share = Fuel_Billboard(**share_info)
        db.session.add(new_share)
        db.session.commit()
        bid =  new_share.id
        fuel_Dtl = dict(
            billboard_id = bid,
            client_id=data['client_id'],
            client_uid=data['client_uid'],
            client_nick = data['client_nick'],
            vehicle_id = data['vehicle_id'],
            vehicle_name = data['vehicle_name'],
            fuel_rate = data['fuel_rate']
        )
        fuel_info = Fuel_BillboardDtl(**fuel_Dtl)
        db.session.add(fuel_info)
        db.session.commit()
        return self.get(data['share_uid'])

    def get_dtl(self, share_uid):
        # r = Fuel_Billboard.query.filter(and_(Fuel_BillboardDtl.billboard_id == Fuel_Billboard, Clients.id == Fuel_BillboardDtl.client_id, Fuel_BillboardDtl.vehicle_id == UserVehicles.id, Fuel_Rate.vehicleId == Fuel_BillboardDtl.vehicle_id)).with_entities(Clients.nickName, UserVehicles.vehicleName, Fuel_Rate.fuelRate, Fuel_Rate.endDate).all()
        b = self.get(share_uid)
        s = Fuel_BillboardDtl.query.filter(Fuel_BillboardDtl.billboard_id == b['id']).join(Clients, Clients.id == Fuel_BillboardDtl.client_id).with_entities(Fuel_BillboardDtl.client_id, Fuel_BillboardDtl.client_uid, Fuel_BillboardDtl.vehicle_id, Fuel_BillboardDtl.vehicle_name, Fuel_BillboardDtl.fuel_rate, Clients.avatarUrl).order_by(Fuel_BillboardDtl.fuel_rate).all()
        dtl =  [x._asdict() for x in s]
        return dict(board= b, detail = dtl)

    def update_board(self, id, **param):
        # print id, param
        s = Fuel_Billboard.query.filter(Fuel_Billboard.id == id).update(param)
        db.session.commit()
        return self.get(s.id)

    def update_detail(self, vehicle_id, fuel_rate, share_uid):
        '''
            更新 最新油耗
        '''
        s = Fuel_BillboardDtl.query.filter(and_(Fuel_BillboardDtl.vehicle_id == vehicle_id)).update(dict(fuel_rate=fuel_rate))
        db.session.commit()
        return self.get_dtl(share_uid)

    def add_fuel_detail(self, **params):
        '''
        '''
        share_uid = params['share_uid']
        b_info = self.get(share_uid)
        id = b_info['id']
        params.pop('share_uid')
        params.update({'billboard_id':id})
        #: find if exists
        vehicle_in_board = Fuel_BillboardDtl.query.filter(and_(
            Fuel_BillboardDtl.billboard_id == id, Fuel_BillboardDtl.vehicle_id == params['vehicle_id']
        ))
        if vehicle_in_board.one_or_none() == None:
            new_obj = Fuel_BillboardDtl(**params)
            db.session.add(new_obj)
        else:
            vehicle_in_board.update(params)
        db.session.commit()
        return self.get_dtl(share_uid)

