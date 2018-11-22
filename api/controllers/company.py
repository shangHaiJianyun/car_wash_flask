# -*- coding: UTF-8 -*-

"""
company.py
- manage company
"""
# import json
# from flask import Blueprint, jsonify, request
from model.models import *


class CompanyM(object):
    def list_all(self):
        company = Company.query.all()
        res = []
        for d in company:
            # print type(d)
            res.append(row2dict(d))
        return res

    def get(self, id):
        res = Company.query.filter(Company.id == id).one_or_none()
        return row2dict(res)

    def add_new(self, **args):
        new_co = Company(**args)
        db.session.add(new_co)
        db.session.commit()
        return self.get(new_co.id)

    def update(self, id, param):
        # print id, param
        new_co = Company.query.filter(Company.id == id).update(param)
        db.session.commit()
        return self.get(new_co.id)

    def delete(self, id):
        tmp = Company.query.filter(Company.id == id)
        db.session.delete(tmp.one())
        db.session.commit()
        return 'success'


class CompanyVehicleM(object):
    def list_vehicles(self, company_id):
        cv = CompanyVehicle.query.filter(
            CompanyVehicle.company_id == company_id).all()
        return row2dict(cv)

    def get(self, id):
        res = CompanyVehicle.query.filter(CompanyVehicle.id == id).one_or_none()
        return row2dict(res)

    def add_vehicle(self, **args):
        cv = CompanyVehicle(**args)
        db.session.add(cv)
        db.session.commit()
        return self.get(cv.id)

    def update(self, id, param):
        # print id, param
        cv = CompanyVehicle.query.filter(Company.id == id).update(param)
        db.session.commit()
        return self.get(cv.id)

    def delete(self, id):
        tmp = CompanyVehicle.query.filter(CompanyVehicle.id == id)
        db.session.delete(tmp.one())
        db.session.commit()
        return 'success'
