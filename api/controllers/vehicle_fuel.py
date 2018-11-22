# -*- coding: UTF-8 -*-

"""
vehicle_fuel.py
- vechicl and fuel functions
"""
from __future__ import division
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from flask import Blueprint, jsonify, request
# from sqlalchemy import *

# import pandas as pd
# import numpy as np
from model.models import *


class VehicleM(object):
    def get(self, id):
        res = UserVehicles.query.filter(UserVehicles.id == id).one_or_none()
        return row2dict(res)

    def create(self, **args):
        new_v = UserVehicles(**args)
        db.session.add(new_v)
        db.session.commit()
        return self.get(new_v.id)

    def update(self, id, param):
        vehicle = UserVehicles.query.filter(
            UserVehicles.id == id).update(param)
        db.session.commit()
        return self.get(id)

    def delete(self, id):
        tmp = UserVehicles.query.filter(UserVehicles.id == id)
        db.session.delete(tmp.one())
        db.session.commit()
        return 'success'

    def user_vehicles(self, user_id):
        vehicles = UserVehicles.query.filter(
            UserVehicles.user_id == user_id).all()
        res = []
        for x in vehicles:
            # print x.id
            res.append(row2dict(x))
        return res


class FuelHisM(object):
    def get(self, id):
        res = FuelHistory.query.filter(FuelHistory.id == id).one_or_none()
        return row2dict(res)

    def get_his(self, vehicle_id, period):
        last_date = datetime.now() - timedelta(days=period)
        # print last_date, 'last_date'
        fuel_his = FuelHistory.query.filter(
            and_(FuelHistory.vehicleId == vehicle_id, FuelHistory.tranDate >= last_date)).all()
        res = []
        for h in fuel_his:
            res.append(row2dict(h))
        return res

    def create(self, **fueldata):
        new_fuel = FuelHistory(**fueldata)
        db.session.add(new_fuel)
        db.session.commit()
        vehicleId = fueldata['vehicleId']
        fuelHis = self.get(new_fuel.id)
        fuelRateHis = update_last_fuel_rate(vehicleId, 0)
        periodFuelRate = cal_period_fuel_rate(vehicleId)
        return dict(fuelHis=fuelHis, fuelRateHis=fuelRateHis, periodFuelRate=periodFuelRate)

    def update(self, id, param):
        fuel_his = FuelHistory.query.filter(
            FuelHistory.id == id).update(param)
        db.session.commit()
        fuelHis = self.get(id)
        vehicleId = fuelHis['vehicleId']
        fuelRateHis = update_last_fuel_rate(vehicleId, 0)
        periodFuelRate = cal_period_fuel_rate(vehicleId)
        return dict(fuelHis=fuelHis, fuelRateHis=fuelRateHis, periodFuelRate=periodFuelRate)

    def delete(self, id):
        tmp = FuelHistory.query.filter(FuelHistory.id == id)
        to_del = tmp.one_or_none()
        if to_del != None:
            vehicleId = row2dict(to_del)['vehicleId']
            db.session.delete(tmp.one())
            db.session.commit()
            fuelRateHis = update_last_fuel_rate(vehicleId, 0)
            periodFuelRate = cal_period_fuel_rate(vehicleId)
            return dict(fuelRateHis=fuelRateHis, periodFuelRate=periodFuelRate)
        else:
            return dict(fuelRateHis={}, periodFuelRate={})


class FSHisM(object):
    '''
        添加 节油大师 的记录
    '''

    def get(self, id):
        res = Fs_History.query.filter(Fs_History.id == id).one_or_none()
        return row2dict(res)

    def get_list(self, vehicleId):
        his = Fs_History.query.filter(Fs_History.vehicleId == vehicleId).all()
        if his:
            return [row2dict(x) for x in his]
        else:
            return ''

    def create(self, **fsdata):
        new_fs = Fs_History(**fsdata)
        db.session.add(new_fs)
        db.session.commit()
        return self.get(new_fs.id)

    def update(self, id, param):
        fs_his = Fs_History.query.filter(
            Fs_History.id == id).update(param)
        db.session.commit()
        return self.get(id)

    def delete(self, id):
        tmp = Fs_History.query.filter(Fs_History.id == id)
        db.session.delete(tmp.one())
        db.session.commit()
        return 'success'


def get_fuelHisDF(vehicleId, period=0):
    if period == 0:
        last_date = date(date.today().year, 1, 1)
    else:
        last_date = datetime.now() - timedelta(days=period)
    his = FuelHistory.query.filter(and_(
        FuelHistory.vehicleId == vehicleId, FuelHistory.tranDate >= last_date)).all()
    his_data = [row2dict(x) for x in his]
    df = pd.DataFrame(his_data)
    if len(df) == 0:
        return df
    df.tranDate = pd.to_datetime(df.tranDate)
    df = df.sort_values(by=['tranDate'], ascending=[1])
    df = df.set_index(df.tranDate)
    return df


def update_last_fuel_rate(vehicleId, period=0):
    '''
        calculate latest fuel_rate 
    '''
    df = get_fuelHisDF(vehicleId, period)
    if len(df) == 0:
        return
    fuel_rate = fuelRate_cal(df, latest=True)
    f = Fuel_Rate.query.filter(Fuel_Rate.vehicleId == vehicleId).one_or_none()
    if f:
        fr = Fuel_Rate.query.filter(
            Fuel_Rate.vehicleId == vehicleId).update(fuel_rate)
    else:
        fr = Fuel_Rate(**fuel_rate)
        db.session.add(fr)
    db.session.commit()
    return fuel_rate


def fuelRate_cal(df, latest=False):
    '''
        计算 df 的油耗
    '''
    tankFull = df.loc[df.tankAlert == True]
    tankEmpty = df.loc[df.fuelAlert == True]
    if latest:
        tankFull = df.loc[df.tankAlert == True][-2:]
        tankEmpty = df.loc[df.fuelAlert == True][-2:]
    fuel_ = dict(
        vehicleId=0,
        startDate=None,
        endDate=None,
        fuelvolume=0,
        amount=0,
        costPerKm=0,
        fuelHisId=0,
        fuelHisIdEnd=0,
        distance=0,
        day_diff=0,
        mileage=0,
        fuelRate=0,
        kmPerDay=0
    )
    if len(tankFull) > 0:
        idx_s = tankFull.index[0]
        idx_e = tankFull.index[-1]
        dff = df.loc[idx_s:idx_e]
        distance = int(dff.iloc[-1].mileage - dff.iloc[0].mileage)
        if distance <= 0:
            return fuel_
        fuelvolume = int(dff[1:].fuelvolume.sum())
        amount = float(dff[1:].amount.sum())
        costPerKm = round(amount / distance, 2)
        fuelHisId = int(dff.iloc[0].id)
        fuelHisIdEnd =int(dff.iloc[-1].id)
        fuelRate = round(fuelvolume * 100 / distance, 2)
        startDate = dff.iloc[0].tranDate.date()
        endDate = dff.iloc[-1].tranDate.date()
        vehicleId = int(dff.iloc[0].vehicleId)
        dd = dff.iloc[-1].tranDate - dff.iloc[0].tranDate
        day_diff = dd.days
        mileage = int(dff.iloc[-1].mileage)
        if day_diff > 0:
            kmPerDay = round(distance / day_diff, 2)
        else:
            kmPerDay = 0
        fuel_rate = dict(
            vehicleId=vehicleId,
            startDate=startDate,
            endDate=endDate,
            fuelvolume=fuelvolume,
            amount=amount,
            costPerKm=costPerKm,
            fuelHisId=fuelHisId,
            fuelHisIdEnd=fuelHisIdEnd,
            distance=distance,
            day_diff=day_diff,
            mileage=mileage,
            fuelRate=fuelRate,
            kmPerDay=kmPerDay
        )
        return fuel_rate            
    elif len(tankEmpty) > 0:
        idx_s = tankEmpty.index[0]
        idx_e = tankEmpty.index[-1]
        dff = df.loc[idx_s:idx_e]
        distance = int(dff.iloc[-1].mileage - dff.iloc[0].mileage)
        if distance <= 0:
            return fuel_
        fuelvolume = int(dff[:-1].fuelvolume.sum())
        amount = float(dff[:-1].amount.sum())
        costPerKm = round(amount / distance, 2)
        fuelHisId = int(dff.iloc[0].id)
        fuelHisIdEnd = int(dff.iloc[-1].id)
        fuelRate = round(fuelvolume * 100 / distance, 2)
        startDate = dff.iloc[0].tranDate.date()
        endDate = dff.iloc[-1].tranDate.date()
        vehicleId = int(dff.iloc[0].vehicleId)
        dd = dff.iloc[-1].tranDate - dff.iloc[0].tranDate
        day_diff = dd.days
        mileage = int(dff.iloc[-1].mileage)
        if day_diff > 0:
            kmPerDay = round(distance / day_diff, 2)
        else:
            kmPerDay = 0
        fuel_rate = dict(
            vehicleId=vehicleId,
            startDate=startDate,
            endDate=endDate,
            fuelvolume=fuelvolume,
            amount=amount,
            costPerKm=costPerKm,
            fuelHisId=fuelHisId,
            fuelHisIdEnd=fuelHisIdEnd,
            distance=distance,
            day_diff=day_diff,
            mileage=mileage,
            fuelRate=fuelRate,
            kmPerDay=kmPerDay
        )
        return fuel_rate
    else:
        return fuel_


def fuel_rate_by_period(df):
    '''
        用于 groupby 计算
    '''
    v = fuelRate_cal(df)
    return pd.Series(v)


def cal_period_fuel_rate(vehicleId):
    '''
        计算 年，季度，月，周 油耗
    '''
    df = get_fuelHisDF(vehicleId, period=0)
    if len(df) > 0:
        period_fuelRate = {}
        for s in ['W', 'M', 'Q', 'A']:
            period_fuel = df.groupby(pd.Grouper(
                freq=s)).apply(fuel_rate_by_period)
            if len(period_fuel) == 0:
                return {}
            period_fuel = period_fuel.dropna()
            if len(period_fuel) == 0:
                return {}
            period_fuel.loc[:, 'fuelPeriod'] = period_fuel.index
            period_fuel.loc[:, 'periodType'] = s
            period_fuel.loc[:, 'periodName'] = period_fuel.index.to_period(
                s).astype(str)
            fuelrate_js = period_fuel.to_json(
                orient='records', date_format='None')
            fuelRateHistory = eval(fuelrate_js)
            for x in fuelRateHistory:
                if s == 'W':
                    x.update(dict(
                        periodName=x['periodName'].replace('\\', '')
                    ))
                x.update(dict(
                    endDate=datetime.fromtimestamp(x['endDate']/1e3),
                    fuelPeriod=datetime.fromtimestamp(x['fuelPeriod']/1e3),
                    startDate=datetime.fromtimestamp(x['startDate']/1e3)
                ))
                if Period_FuelRate.query.filter(and_(Period_FuelRate.periodType == s, Period_FuelRate.periodName == x['periodName'])).one_or_none():
                    Period_FuelRate.query.filter(and_(
                        Period_FuelRate.periodType == s, Period_FuelRate.periodName == x['periodName'])).update(x)
                else:
                    newObj = Period_FuelRate(**x)
                    db.session.add(newObj)
                db.session.commit()
            period_fuelRate.update({s: fuelRateHistory})
        return period_fuelRate
    else:
        return {}


def get_last_fuelrate(vehicleId):
    his = Fuel_Rate.query.filter(
        Fuel_Rate.vehicleId == vehicleId).one_or_none()
    if his:
        fuelRateHis = row2dict(his)
    else:
        fuelRateHis = None
    return fuelRateHis


def get_period_fuelrate(vehicleId):
    t = date(date.today().year, 1, 1)
    fr = Period_FuelRate.query.filter(and_(
        Period_FuelRate.vehicleId == vehicleId, Period_FuelRate.startDate > t)).all()
    if fr:
        s = [row2dict(x) for x in fr]
        fk = dict(W=[], M=[], Q=[], A=[])
        for x in s:
            key = x['periodType']
            fk[key].append(x)
        return fk
    else:
        return None


def list_all_vehicle():
    vehicles = UserVehicles.query.all()
    res = []
    for d in vehicles:
        res.append(row2dict(d))
    return res


class FuelTypeM(object):
    def get_all(self):
        fuels = FuelType.query.all()
        res = []
        fuelName = []
        fuelTypeId = []
        for d in fuels:
            f = row2dict(d)
            res.append(f)
            fuelName.append(f['fuelTypeName'])
            fuelTypeId.append(f['id'])
        return dict(fuelName=fuelName, fuelTypeId=fuelTypeId)

    def create(self, **fuelType):
        new_type = FuelType(**fuelType)
        db.session.add(new_type)
        db.session.commit()
        return self.get_all()
