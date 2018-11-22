# -*- coding: UTF-8 -*-
"""
models.py
- Data classes for the surveyapi application
"""
# from flask import Blueprint, request, current_app
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from passlib.apps import custom_app_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from flask import current_app
from sqlalchemy import *


app = current_app
db = SQLAlchemy()


def row2dict(row):
    if row is None:
        return ""
    d = {}
    for column in row.__table__.columns:
        if isinstance(getattr(row, column.name), unicode):
            d[column.name] = getattr(row, column.name)
        elif isinstance(getattr(row, column.name), datetime):
            d[column.name] = str(getattr(row, column.name))
        else:
            # d[column.name] = str(getattr(row, column.name))
            d[column.name] = getattr(row, column.name)
    return d


class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_on = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())


UserRoles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('user_group.id'))
)


class User(Base, db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(32))
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(32))
    phone = db.Column(db.String(32))
    wxid = db.Column(db.String(128))
    xcxid = db.Column(db.String(128))
    UnionID = db.Column(db.String(128))
    wxName = db.Column(db.String(50))
    wxpicurl = db.Column(db.String(128))
    roles = db.relationship(
        'Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.username


class Role(Base, db.Model, RoleMixin):
    __tablename__ = 'user_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return '<UserGroup %r>' % self.name


# for flask-security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class Clients(Base, db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    UnionID = db.Column(db.String(128))
    wxId = db.Column(db.String(128))
    xcxId = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    registed_on = db.Column(db.DateTime, default=datetime.now)
    name = db.Column(db.String(60))
    nickName = db.Column(db.String(60))
    phone = db.Column(db.String(30))
    gender = db.Column(db.String(10))
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    avatarUrl = db.Column(db.String(128))
    parent_userid = db.Column(db.Integer)
    notes = db.Column(db.String(128))

    # def __repr__(self):
    #     return '<Client %r>' % self.name


class FuelType(db.Model):
    __tablename__ = 'fuel_type'
    id = db.Column(db.Integer, primary_key=True)
    fuelTypeName = db.Column(db.String(50, convert_unicode=True))
    notes = db.Column(db.String(100))
    sort_seq = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # def __repr__(self):
    #     return '<FuelType %r>' % self.fuelTypeName


class UserVehicles(Base, db.Model):
    __tablename__ = 'user_vehicles'

    id = db.Column(db.Integer, primary_key=True)
    vehicleName = db.Column(db.String(50))
    brand = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    engine = db.Column(db.Float, default=0)
    weight = db.Column(db.Float, default=0)
    tankVol = db.Column(db.Float, default=0)
    calTankVol = db.Column(db.Float, default=0)
    startMileage = db.Column(db.Float, default=0)
    lastMileage = db.Column(db.Float, default=0)
    lastFuelRate = db.Column(db.Float, default=0)
    lastFuelDate = db.Column(db.DateTime)
    lpn = db.Column(db.String(50))
    notes = db.Column(db.String(128))
    fuelType = db.Column(db.Integer)
    registed_on = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)
    is_car = db.Column(db.Boolean, default=True)

    # def __repr__(self):
    #     return '<UserVehicles %r>' % self.vehicleName


class FuelHistory(Base, db.Model):
    __tablename__ = 'fuel_history'

    id = db.Column(db.Integer, primary_key=True)
    vehicleId = db.Column(db.Integer)
    tranDate = db.Column(db.DateTime, default=datetime.now)
    amount = db.Column(db.Float, default=0)
    price = db.Column(db.Float, default=0)
    fuelvolume = db.Column(db.Float, default=0)
    fuelTypeId = db.Column(db.Integer)
    mileage = db.Column(db.Float, default=0)
    tankStatus = db.Column(db.Integer, default=0)
    fuelAlert = db.Column(db.Boolean, nullable=False, default=False)
    tankAlert = db.Column(db.Boolean,  default=False)
    calculated = db.Column(db.Boolean, nullable=False, default=False)


class Fs_History(Base, db.Model):
    __tablename__ = 'fs_history'
    id = db.Column(db.Integer, primary_key=True)
    vehicleId = db.Column(db.Integer)
    tranDate = db.Column(db.DateTime, default=datetime.now)
    amount = db.Column(db.Float, default=0)
    price = db.Column(db.Float, default=0)
    qty = db.Column(db.Float, default=0)
    mileage = db.Column(db.Float, default=0)


class FuelHisPic(db.Model):
    __tablename__ = 'fuel_his_pic'

    id = db.Column(db.Integer, primary_key=True)
    fuelHisId = db.Column(db.Integer)
    picUrl = db.Column(db.String(128))
    notes = db.Column(db.String(50))


class Fuel_Rate(db.Model):
    __tablename__ = 'fuel_rate'

    id = db.Column(db.Integer, primary_key=True)
    vehicleId = db.Column(db.Integer)
    startDate = db.Column(db.DateTime)
    endDate = db.Column(db.DateTime)
    fuelvolume = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, default=0)
    costPerKm = db.Column(db.Float, default=0)
    kmPerDay = db.Column(db.Float, default=0)
    fuelRate = db.Column(db.Float, default=0)
    distance = db.Column(db.Float, default=0)
    day_diff = db.Column(db.Float, default=0)
    mileage = db.Column(db.Float, default=0)
    fuelHisId = db.Column(db.Integer)
    fuelHisIdEnd = db.Column(db.Integer)


class Period_FuelRate(db.Model):
    __tablename__ = 'period_fuel_rate'

    id = db.Column(db.Integer, primary_key=True)
    periodType = db.Column(db.String(10))
    periodName = db.Column(db.String(25))
    fuelPeriod = db.Column(db.DateTime)
    vehicleId = db.Column(db.Integer)
    startDate = db.Column(db.DateTime)
    endDate = db.Column(db.DateTime)
    fuelvolume = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, default=0)
    costPerKm = db.Column(db.Float, default=0)
    kmPerDay = db.Column(db.Float, default=0)
    fuelRate = db.Column(db.Float, default=0)
    distance = db.Column(db.Float, default=0)
    day_diff = db.Column(db.Float, default=0)
    mileage = db.Column(db.Float, default=0)
    fuelHisId = db.Column(db.Integer)
    fuelHisIdEnd = db.Column(db.Integer)    


class Fuel_Billboard(Base, db.Model):
    __tablename__ = 'fuel_billboard'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    share_uid = db.Column(db.String(128))
    client_uid = db.Column(db.String(128))
    client_nick = db.Column(db.String(60))

class Fuel_BillboardDtl(db.Model):
    __tablename__ = 'fuel_billboard_dtl'
    id = db.Column(db.Integer, primary_key=True)
    billboard_id = db.Column(db.Integer)
    client_id = db.Column(db.Integer)
    client_uid = db.Column(db.String(128))
    vehicle_id = db.Column(db.Integer)
    updated_on = db.Column(db.DateTime)
    client_nick = db.Column(db.String(60))
    vehicle_name = db.Column(db.String(60))
    fuel_rate = db.Column(db.Float)


class ClientSystem(db.Model):
    __tablename__ = 'client_system'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    phone_SDKVersion = db.Column(db.String(128))
    errMsg = db.Column(db.String(128))
    brand = db.Column(db.String(128))
    phone_fontSizeSetting = db.Column(db.String(128))
    user_language = db.Column(db.String(128))
    phone_name = db.Column(db.String(128))
    phone_pixelRatio = db.Column(db.String(128))
    phone_platform = db.Column(db.String(128))
    phone_screenHeight = db.Column(db.String(128))
    phone_screenWidth = db.Column(db.String(128))
    phone_system = db.Column(db.String(128))
    phone_version = db.Column(db.String(128))
    phone_windowHeight = db.Column(db.String(128))
    phone_windowWidth = db.Column(db.String(128))


class Company(Base, db.Model):
    __tablename__ = 'company'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    address = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    province = db.Column(db.String(50))
    city = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    qr_url = db.Column(db.String(128))
    qr_expireDate = db.Column(db.DateTime)

    # def __repr__(self):
    #     return '<Company %r>' % self.name


class UserCompany(Base, db.Model):
    __tablename__ = 'user_company'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class CompanyVehicle(Base, db.Model):
    __tablename__ = 'company_vehicle'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer)
    vehicle_lpn = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
