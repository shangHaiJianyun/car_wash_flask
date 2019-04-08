# -*- coding: utf-8 -*-
'''
  用于创建模拟派单的数据
'''
import math
import datetime as dt
import time
import random
import json
import numpy as np
import pandas as pd

from api.models.models import *


def random_period(day_str):
    t = datetime.strptime(day_str + ' 6:00', "%Y-%m-%d %H:%M")
    p = random.randint(0, 14)
    t1 = dt.timedelta(seconds=3600 * p)
    start = t + t1
    if p < 14:
        p2 = random.randint(2, 16 - p)
    else:
        p2 = 2
    end = start + dt.timedelta(seconds=3600 * p2)
    return start, end


def gen_client_orders(regions, workday, n_order, n_address):
    '''
        gen orders to simulate

        output:
            order array:
                job_type: 2: 20min, 3:30min, 4:40min
    '''
    def job_bucket(end_time):
        return time_bkt[np.argmin(np.abs(time_bkt - end_time))]

    orders = []

    for x in range(n_order - 1):
        start_time, end_time = random_period(workday)
        job_type = random.randint(2, 4)
        hrs = (job_type * 600) / 3600
        addr = random.randint(1, n_address)
        if len(regions) < 2:
            region_id = regions[0]
        else:
            region_id = regions[random.randint(0, len(regions) - 1)]
        orders.append({
            'city': u"上海市",
            'region_id': region_id,
            'order_id': x,
            'addr': addr,
            'start_time': start_time,
            #             'late_start': late_start,
            'end_time': end_time,
            'job_type': job_type,
            'hrs': hrs,
            'ts': end_time - start_time,
        })
    jobs = pd.DataFrame([x for x in orders])
    jobs.loc[:, 'hrs_t'] = jobs.hrs.apply(
        lambda x: dt.timedelta(seconds=x * 3600))
    return jobs


def gen_worker(regions, day_str, n_worker):
    '''
        worker_type: 
        1: 全职 
        2: 兼职 
        3: 特服

        min_hrs : bdt 应派工时
        mdt_hrs: 技师名下订单工时
    '''
    workers = []
    for w in range(n_worker):
        tp = random.randint(1, 20)
        w_rank = random.randint(100, 500)
        if len(regions) < 2:
            region_id = regions[0]
        else:
            region_id = regions[random.randint(0, len(regions) - 1)]
        if tp % 4 == 1:
            worker_type = 2
            w_type = u'兼职'
            s1 = random.randint(0, 8)
            w_start = dt.datetime.strptime(
                day_str + ' 6:00', "%Y-%m-%d %H:%M") + dt.timedelta(seconds=3600*s1)
            w_end = w_start + dt.timedelta(seconds=3600*4)
            w_hrs = 4
            max_star_t = random.randint(2, 4)
            mdt = random.randint(0, 8)
        elif tp % 5 == 0:
            worker_type = 3
            w_type = u'特服'
            w_start = dt.datetime.strptime(day_str + ' 6:00', "%Y-%m-%d %H:%M")
            w_end = w_start + dt.timedelta(seconds=3600*1*8)
            w_hrs = 8
            max_star_t = 8
            mdt = 0
            w_rank = 0
        else:
            s1 = random.randint(0, 8)
            worker_type = 1
            w_type = u'全职'
            w_start = dt.datetime.strptime(
                day_str + ' 6:00', "%Y-%m-%d %H:%M") + dt.timedelta(seconds=3600*s1)
            w_end = w_start + dt.timedelta(seconds=3600*1*8)
            w_hrs = 8
            max_star_t = random.randint(4, 8)
            mdt = random.randint(0, 12)

        workers.append({
            'city': u"上海市",
            'worker_id': w + 1,
            'w_start': w_start,  # ： 工作开始时间
            'w_end': w_end,  # ：工作结束时间
            'worker_type': worker_type,
            # 'w_type': w_type,
            'w_hrs': w_hrs,  # 可用工时
            'w_region': region_id,  # 开工地点(区域id)
            'w_rank': w_rank,  # 星级
            'max_star_t': max_star_t,  # 按星级最大派单工时
            'mdt': mdt,  # 技师名下订单
            'hrs_to_assign': 0,
            'hrs_assigned': 0
        })
    workers = pd.DataFrame([wr for wr in workers]).sort_values(
        ['worker_type', 'w_start', 'w_region'])
    #: 确定最小派单工时
    workers.loc[:, 'min_hrs'] = np.where(
        workers.max_star_t < workers.w_hrs, workers.max_star_t, workers.w_hrs)
    workers.loc[:, 'bdt_hrs'] = np.where(
        workers.mdt < workers.min_hrs, workers.mdt, workers.min_hrs)
    workers = workers.sort_values(
        ['worker_type', 'hrs_to_assign', 'w_rank'], ascending=[1, 0, 0])
    return workers
