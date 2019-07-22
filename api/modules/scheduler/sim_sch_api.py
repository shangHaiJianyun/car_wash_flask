# -*- coding: utf-8 -*-
"""
new sch funciton

functions:
process_unpaid_orders：
    自动获取未付款订单，将订单设置为已付款


"""
import requests
import datetime as dt

from api.modules.scheduler.sch_api import create_dispatch, process_unpaid_orders, save_data_from_api
from .sch_lib import *
from .sch import *
from api.common_func.cluster_address import cluster


def cluster_addr(addr_list):
    print(addr_list)
    print(addr_list.shape)
    addr_labels, lat_label = cluster(addr_list)
    return lat_label


def sch_jobs_today():
    """
        派当日订单， 当前时间以后的
    """
    # 获取数据，更新到db
    process_unpaid_orders()
    r = save_data_from_api()
    city = "上海市"
    sch_datetime = dt.datetime.today()
    # ：test data
    # sch_datetime = dt.datetime(2019, 4, 9, 11, 00)
    day_str = sch_datetime.date().isoformat()
    sch_jobs = SchJobs(city)
    jobs = sch_jobs.unscheduled_jobs(sch_datetime)
    if jobs is None:
        return dict(status='error', msg='no jobs', data='')
    sch_workers = SchWorkers(city)
    workers = sch_workers.all_worker_by_date(day_str)
    if workers is None:
        return dict(status='error', msg='no workers', data='')
    assigned_jobs, open_jobs, worker_summary, arranged_workers = dispatch_region_jobs(
        jobs, workers, day_str)

    if not open_jobs.empty:
        open_jobs_dict = open_jobs.drop(['hrs_t'], 1).to_dict('records')
    else:
        open_jobs_dict = {}

    if assigned_jobs.empty:
        return dict(status='success', data=dict(
            workers=arranged_workers.to_dict('records'),
            open_jobs=open_jobs_dict
        )
                    )
    else:
        assigned_jobs = assigned_jobs.drop(['hrs_t'], 1)
        #: create dispatch data
    deadline = 15
    disps = create_dispatch(worker_summary, assigned_jobs, day_str, deadline)
    return dict(status='success',
                data=dict(
                    assigned_jobs=assigned_jobs.to_dict('records'),
                    workers=arranged_workers.to_dict('records'),
                    open_jobs=open_jobs.to_dict('records'),
                    worker_summary=worker_summary.to_dict('records'),
                    dispatch_data=disps)
                )


def sch_tomorrow_by_region(task_id, region_id, day_str, city="上海市"):
    """
        temp: 派明天订单， 
    """
    # 获取数据，region Jobs
    region_jobs = SchJobsM.find(sch_task_id=task_id, region_id=region_id)

    region_worker = SchWorkersM.find(w_region=region_id, sch_date=day_str, city=city).all()

    if region_jobs is None:
        return dict(status='error', msg='no jobs', data='')
    sch_workers = SchWorkers(city)
    workers = sch_workers.all_worker_by_date(day_str)
    if workers is None:
        return dict(status='error', msg='no workers', data='')
    # return "Done"
    assigned_jobs, open_jobs, worker_summary, arranged_workers = dispatch_region_jobs(
        region_jobs, workers, day_str)
    if not open_jobs.empty:
        open_jobs_dict = open_jobs.drop(['hrs_t'], 1).to_dict('records')
    else:
        open_jobs_dict = {}

    if assigned_jobs.empty:
        return dict(status='success', data=dict(
            workers=arranged_workers.to_dict('records'),
            open_jobs=open_jobs_dict
        )
                    )
    else:
        assigned_jobs = assigned_jobs.drop(['hrs_t'], 1)
    #: create dispatch data
    deadline = 60
    disps = create_dispatch(worker_summary, assigned_jobs, day_str, deadline)
    return dict(status='success',
                data=dict(
                    assigned_jobs=assigned_jobs.to_dict('records'),
                    workers=arranged_workers.to_dict('records'),
                    open_jobs=open_jobs.to_dict('records'),
                    worker_summary=worker_summary.to_dict('records'),
                    dispatch_data=disps)
                )


def dispatch_to_api(data, disp_id, disp_sch):
    passwd = 'xunjiepf'
    dispatch_data = data
    dispatch_data.update(passwd=passwd)
    req = requests.post(
        url='https://banana.xunjiepf.cn/api/dispatch/dispatchorder',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(dispatch_data)
    )
    if req.status_code == requests.codes.ok:
        res = req.json()
        if res[0]['errcode'] == 0:
            dispatch_num = res[0]['dispatch_id']
            disp_sch.update_dispatched(disp_id, 'dispatched', dispatch_num)
            return "success"
        else:
            slog = SchTestLog()
            data.update(errcode=res[0]['errcode'])
            slog.create('dispatch_err', data)
            return "error"
    else:
        slog = SchTestLog()
        slog.create('dispatch_err', 'request fail')
        return "error"

# def dispatch_jobs(data, disp_id):
#     """派单内容"""
#     passwd = 'xunjiepf'
#     # 获取传输参数

#     disp_success = []
#     disp_error = []

#     for y in data:
#         x = y
#         x.update(passwd=passwd)
#         print(x)
#         req = requests.post(
#             url='https://banana.xunjiepf.cn/api/dispatch/dispatchorder',
#             headers={
#                 "Content-Type": "application/json"
#             },
#             data=json.dumps(x)
#         )
#         if req.status_code == requests.codes.ok:
#             res = res.json()
#             if res['errcode'] == 0:
#                 disp_success.append(y)
#             else:
#                 disp_error.append(dict(data=y, error=res['errmsg']))
#         else:
#             disp_error.append(dict(data=y, error='request fail'))
#     return dict(disp_success=disp_success, disp_error=disp_error, total=len(x), error_count=len(disp_error), succes_count=len(disp_success))
