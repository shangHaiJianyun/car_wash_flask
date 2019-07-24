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
import api.common_func.area as my_area
from .sch_api import *
# from .to_task import *
from api.new_task import *
from api.common_func.cluster_address import cluster


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
        sim_addr = my_area.gen_loc(region_id)
        address = sim_addr[1]
        lat, lon = sim_addr[0].split(',')
        orders.append({
            'city': u"上海市",
            'region_id': region_id,
            'order_id': random.randint(10000, 20000),
            'address': address,
            'addr': '',
            'start_time': start_time,
            'end_time': end_time,
            'job_type': job_type,
            'hrs': hrs,
            'addr_lat': lat,
            'addr_lon': lon
        })
    jobs = pd.DataFrame([x for x in orders])
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
            worker_type = 3
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
            'hrs_assigned': 0,
            'adt_hrs': 0
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


def start_multi_region_sch(city, sch_date_str):
    """
        multi region sch main
    """
    #: create SchTask
    task_name = 'schedule of ' + dt.datetime.today().date().isoformat()
    # st = SchTask(city)

    # sch_task_id = st.create(sch_date_str, task_name)

    sch_dt = dt.datetime.strptime(sch_date_str,  "%Y-%m-%d")
    new_task = SchTaskM(city=city, sch_date=sch_date_str,
                        name=task_name, status='started')
    db.session.add(new_task)
    db.session.flush()
    sch_task_id = new_task.id
    #: mark job data, count region
    sh = SchJobs(city)
    region_counts = sh.mark_unsch_jobs(sch_dt, sch_task_id)

    #: create subtask by region
    if region_counts is None:
        return dict(message='no open jobs')

    for r in region_counts:
        region_id = r['region_id']
        region_jobs_count = r['region_jobs']
        sub_task_uid = str(sch_task_id) + '-' + region_id

    # issue region sch 使用 celery task
        # celery_task = region_job_sch.delay(sch_task_id, sch_date_str, region_id)
        # sub_task_uid = celery_task.id

    #: create sub_task records
        st = SubTaskM(
            city=city,
            sch_task_id=sch_task_id,
            sub_task_uid=sub_task_uid,
            sch_date=sch_dt,
            status='started',
            region_id=region_id,
            job_num=region_jobs_count
        )
        db.session.add(st)
        db.session.flush()

    #: 按 region 派单 不使用 celery
        sch_tomorrow_by_region(sch_task_id, region_id,
                               sub_task_uid, sch_date_str, city="上海市")

    db.session.commit()
    return


def update_celety_status(celery_uid, data):
    """
        update celery task result
    """
    sub_task = SubTaskM.find(sub_task_uid=celery_uid)
    if sub_task.one_or_none():
        sub_task.update(data)
        db.session.commit()
        return row2dict(sub_task.one())
    else:
        return


def check_task_status(sch_task_id):
    """
        check task 's all sub, decide next step
    """
    sub_tasks = SubTaskM.find(sch_task_id=sch_task_id, status='started').all()
    if len(sub_tasks) == 0:
        sch_task = SchTaskM.find(id=sch_task_id).one_or_none()
        if sch_task:
            sch_task.update(dict(status='stage2'))
            schedule_step2(sch_task_id)
            db.session.commit()


def sch_tomorrow_by_region(task_id, region_id, celery_uid, sch_date_str, city="上海市"):
    """
        step1: 按region 派单
    """
    # 获取数据，region Jobs
    sch_job = SchJobs(city)
    region_jobs = sch_job.get_open_job_by_task_region(task_id, region_id)

    if region_jobs is None:
        data = dict(job_num=0, status='done', sub_task_message='no open jobs')
        update_celety_status(celery_uid, data)
        check_task_status(task_id)
        return dict(status='error', msg='no jobs', data='')

    job_num = len(region_jobs)
    df_addr = region_jobs.groupby('address').agg(
        {"addr_lat": 'last', 'addr_lon': 'last'})
    X = np.array(df_addr)
    #: Cluster Addr
    addr_labels, lat_label = cluster(X)
    # addr_labels = cluster_addr(X)
    df_addr.loc[:, 'addr'] = addr_labels
    region_jobs = pd.merge(region_jobs, df_addr, how='left', left_on='address',
                           left_index=False, right_index=True, sort=True,
                           suffixes=('', '_y'), copy=True, indicator=False,
                           validate=None)
    region_jobs.loc[:, 'addr'] = region_jobs.addr_y
    region_jobs = region_jobs.loc[:,
                                  (u'addr', u'end_time', u'hrs', u'job_type', u'order_id', u'region_id', 'hrs_t',
                                   u'sch_task_id', 'status', u'city', 'sch_date', u'start_time', u'worker_id', u'addr_lat', u'addr_lon')]
    sch_workers = SchWorkers(city)
    region_wkrs = sch_workers.all_worker_by_date(sch_date_str, region_id)
    if region_wkrs is None:
        data = dict(job_num=job_num, status='done',
                    sub_task_message='no free worker')
        update_celety_status(celery_uid, data)
        check_task_status(task_id)
        return dict(status='error', msg='no workers', data='')

    # return "Done"
    assigned_jobs, open_jobs, worker_summary, arranged_workers = dispatch_region_jobs(
        region_jobs, region_wkrs, sch_date_str)

    # update assigned_jobs to  database
    if not assigned_jobs.empty:
        save_assign_jobs_db(assigned_jobs)

    if not open_jobs.empty:
        # open_jobs_dict = open_jobs.drop(['hrs_t'], 1).to_dict('records')
        open_job_num = len(open_jobs)
    else:
        open_job_num = 0
    data = dict(job_num=job_num, open_job_num=open_job_num,
                status='done', sub_task_message='step 1 done')
    update_celety_status(celery_uid, data)
    return


def schedule_step2(sch_task_id, city="上海市"):
    """
    activated by last region schedule task
    """
    sch_job = SchJobs(city)
    sch_workers = SchWorkers(city)

    open_jobs = sch_job.get_open_job_by_task_region(sch_task_id)
    if open_jobs is None:
        return
    sch_date_str = open_jobs.iloc[0].sch_date

    if len(open_jobs):
        #: sort by region
        open_by_region = open_jobs.groupby('region_id').agg({
            'order_id': 'count',
            'start_time': np.min,
            'end_time': np.max,
            'hrs': 'sum'
        }).sort_values(['hrs'], ascending=[0])

        #: iter by region
        #: find near area
        for idx, row in open_by_region.iterrows():
            nearby_list = near_area_data(idx)
            #: get region_jobs open
            region_jobs = open_jobs.loc[open_jobs.region_id == idx]

            #: get nearby worker
            for n in nearby_list:
                near_region_id = n['area_id']
                ridding_time = n['ridding_time']
                region_wkrs = sch_workers.all_worker_by_date(
                    sch_date_str, near_region_id)
                if region_wkrs is not None:
                    assigned_jobs, open_jobs, worker_summary, arranged_workers = dispatch_region_jobs(
                        region_jobs, region_wkrs, sch_date_str)
                    if assigned_jobs is not None:
                        save_assign_jobs_db(assigned_jobs)

    return sch_task_id


def save_assign_jobs_db(assigned_jobs):
    """
        save assigned_jobs dataframe to db
    """
    if 'grp' in assigned_jobs:
        assigned_jobs = assigned_jobs.drop(
            ['grp', 'hrs_t', 'trans_hr', 'wait_hr'], 1)
    assigned_jobs.start_time = assigned_jobs.start_time.apply(
        lambda x: x.strftime('%Y-%m-%d %H:%M'))
    assigned_jobs.end_time = assigned_jobs.end_time.apply(
        lambda x: x.strftime('%Y-%m-%d %H:%M'))
    assigned_jobs.plan_end = assigned_jobs.plan_end.apply(
        lambda x: x.strftime('%Y-%m-%d %H:%M'))
    assigned_jobs.plan_start = assigned_jobs.plan_start.apply(
        lambda x: x.strftime('%Y-%m-%d %H:%M'))
    assigned_jobs.status = 'assigned'

    to_update = assigned_jobs.to_dict('records')
    for x in to_update:
        SchJobsM.query.filter(SchJobsM.order_id == x['order_id']).update(x)
        db.session.flush()
    try:
        db.session.commit()
    except:
        db.session.rollback()
    return 'ok'


def near_area_data(region_id):
    """
    return:
        [
        {'area_id': 439, 'ridding_time': 1349}, 
        {'area_id': 441, 'ridding_time': 1544}, 
        {'area_id': 410, 'ridding_time': 1594}, 
        {'area_id': 470, 'ridding_time': 1618}, 
        {'area_id': 411, 'ridding_time': 2089}, 
        {'area_id': 471, 'ridding_time': 2112}, 
        {'area_id': 409, 'ridding_time': 2281}, 
        {'area_id': 469, 'ridding_time': 3229}
        ]
    """
    n_area = my_area.NearbyM()

    _nears = n_area.get_nearby(region_id)['nearby']
    nearby_list = []
    for (k, v) in _nears.items():
        if bool(v):
            nearby_list.append(
                dict(area_id=v['area_id'], ridding_time=v['ridding_time']))
    print(nearby_list)
    nearby_list = sorted(nearby_list, key=lambda x: x['ridding_time'])
    return nearby_list
