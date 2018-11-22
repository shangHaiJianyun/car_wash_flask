# -*- coding: UTF-8 -*-

"""
vehicle_maintenance.py
- vechicl maintenance functions
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
