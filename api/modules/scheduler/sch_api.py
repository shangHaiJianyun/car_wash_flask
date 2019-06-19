# -*- coding: utf-8 -*-
"""
get data from php backend
save data to python backend

functions:
process_unpaid_orders：
    自动获取未付款订单，将订单设置为已付款


"""
import requests
import datetime as dt
from .sch_lib import *
from .sch import *
from api.common_func.cluster_address import cluster


def get_orders_from_api(days=2, city="上海市"):
    """
        get paied orders
    input:
        days: 天数
    output：
        order list
    """
    access_key = 'xunjiepf'
    url = "https://banana.xunjiepf.cn/api/extend/getorderlist"
    order_status = 2
    yd = dt.datetime.today() - dt.timedelta(days=2)
    start_service_date = yd.date().isoformat()
    tm = dt.datetime.today() + dt.timedelta(days=days + 1)
    end_service_date = tm.date().isoformat()
    data = {
        'access_key': access_key,
        'order_status': order_status,
        'start_service_date': start_service_date,
        'end_service_date': end_service_date
    }
    res = requests.post(
        url,
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )
    result = res.json()['data']['data']
    if res.json()['data']['page_count'] > 1:
        page_size = res.json()['data']['total_count']
        data.update(page_size=page_size)
        res = requests.post(
            url,
            headers={
                "Content-Type": "application/json"
            },
            data=json.dumps(data)
        )
        result = res.json()['data']['data']
    return result


def save_order_from_api(sch_task_id, order_list, city="上海市"):
    """
        convert datetime to string format
    """
    df = pd.DataFrame(order_list)
    df.loc[:, 'addr_lat'] = df.address_latitude.astype(float)
    df.loc[:, 'addr_lon'] = df.address_longitude.astype(float)
    df.loc[:, 'region_id'] = '0'
    df.loc[:, 'city'] = city
    df.loc[:, 'worker_id'] = '0'
    df.loc[:, 'sch_task_id'] = sch_task_id
    df.loc[:, 'status'] = 'open'
    df.loc[:, 'start_time'] = df.service_date + ' ' + df.start_time
    df.loc[:, 'end_time'] = df.service_date + ' ' + df.end_time
    # df.loc[:, 'start_time'] = pd.to_datetime(
    #     df.service_date + ' ' + df.start_time, format="%Y-%m-%d %H:%M")
    # df.loc[:, 'end_time'] = pd.to_datetime(
    #     df.service_date + ' ' + df.end_time, format="%Y-%m-%d %H:%M")
    df.loc[:, 'sch_date'] = df.service_date
    df.loc[:, 'hrs'] = pd.to_numeric(df.item_duration)
    df = df.rename(columns={
        'item_id': 'job_type'
    })
    #: get unique address_id
    df_addr = df.groupby('address_id').agg(
        {"addr_lat": 'last', 'addr_lon': 'last'})
    X = np.array(df_addr)
    #: Cluster Addr
    addr_labels = cluster_addr(X)
    df_addr.loc[:, 'addr'] = addr_labels
    df = pd.merge(df, df_addr, how='left', left_on='address_id',
                  left_index=False, right_index=True, sort=True,
                  suffixes=('', '_y'), copy=True, indicator=False,
                  validate=None)
    df = df.loc[:, (u'addr', u'end_time', u'hrs', u'job_type', u'order_id', u'region_id', u'sch_task_id',
                    'status', u'city', 'sch_date', u'start_time', u'worker_id', u'addr_lat', u'addr_lon')]
    Sch_J = SchJobs(city)
    res = Sch_J.df_insert(df)
    return res['status']


def cluster_addr(addr_list):
    print(addr_list)
    print(addr_list.shape)
    addr_labels, lat_label = cluster(addr_list)
    return lat_label


def save_workers_from_api(day_str, city="上海市"):
    """
        get available worker and save to database
    """

    access_key = 'xunjiepf'
    date = day_str
    results = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getworkerlist",
        params={
            'access_key': access_key,
            'city': city,
            'date': day_str
        }
    )
    # datas = results.json()
    # print(datas)
    page_size = results.json()['data']['total_count']

    res = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getworkerlist",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({
            'access_key': access_key,
            'page_size': page_size,
            'city': city,
            "date": date
        })
    )
    workers = res.json()['data']['data']
    #: prepare dataframe
    df = pd.DataFrame(workers)
    df = df.loc[(df.auth_state == "3") & (df.is_holiday == "1") & (
            df.service_start_time != "") & (df.service_end_time != "")]
    df = df.loc[:, ('uid', 'service_start_time',
                    'service_end_time', 'worker_type')]
    df.loc[:, 'worker_id'] = df.uid
    df.loc[:, 'w_region'] = '0'
    df.loc[:, 'city'] = city
    df.loc[:, 'sch_date'] = day_str
    df.loc[:, 'w_start'] = day_str + ' ' + df.service_start_time
    df.loc[:, 'w_end'] = day_str + ' ' + df.service_end_time

    df.loc[:, 'w_start_t'] = pd.to_datetime(
        day_str + ' ' + df.service_start_time, format="%Y-%m-%d %H:%M")
    df.loc[:, 'w_end_t'] = pd.to_datetime(
        day_str + ' ' + df.service_end_time, format="%Y-%m-%d %H:%M")
    df.loc[:, 'w_hrs'] = (df.w_end_t - df.w_start_t) / np.timedelta64(60, 'm')
    df.loc[:, 'w_rank'] = 100
    df.loc[:, 'w_type'] = df.worker_type
    df.loc[:, 'worker_type'] = 1
    df.loc[:, 'mdt'] = 8
    df.loc[:, 'max_star_t'] = 8
    df.loc[:, 'hrs_to_assign'] = 0
    df.loc[:, 'hrs_assigned'] = 0
    df.loc[:, 'adt_hrs'] = 0
    df.loc[:, 'min_hrs'] = np.where(
        df.max_star_t < df.w_hrs, df.max_star_t, df.w_hrs)
    df.loc[:, 'bdt_hrs'] = np.where(
        df.mdt < df.min_hrs, df.mdt, df.min_hrs)
    df = df.loc[:,
         (u'hrs_assigned', u'hrs_to_assign', u'max_star_t', u'mdt', u'w_end', u'w_hrs', 'sch_date', 'worker_id',
          u'w_rank', 'city', u'w_region', u'w_start', u'w_type', u'worker_type', u'min_hrs', u'bdt_hrs', 'adt_hrs')]
    # return df
    # print(df.loc[:, ('city', 'worker_id')])
    Sch_W = SchWorkers(city)
    res = Sch_W.df_insert(df)
    return res['status']


def process_unpaid_orders():
    access_key = 'xunjiepf'
    url = "https://banana.xunjiepf.cn/api/extend/getorderlist"
    data = {
        'access_key': access_key
    }
    res = requests.post(
        url,
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(data)
    )
    result = res.json()['data']['data']
    data = []
    for i in result:
        if int(i['order_status']) == 1:
            data.append(i)
    paid_order = []
    for x in data[:2]:
        order_ids = x["order_id"]
        res = set_order_paid(order_ids)
        if res:
            paid_order.append(x)
    stl = SchTestLog()
    stl.create("Auto_Pay", dict(orders=paid_order))
    return paid_order


def set_order_paid(order_ids):
    access_key = 'xunjiepf'
    params = {
        "access_key": access_key,
        "order_ids": order_ids,
        "order_status": 2
    }
    res = requests.post(
        url='https://banana.xunjiepf.cn/api/extend/updateOrderStatus',
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps(params)
    )
    if res.json()["errcode"] == 0:
        return order_ids
    else:
        return False


def save_data_from_api():
    """
         从 php 获取 技师 和 订单数据，保存到 派单系统
    """
    joblist = get_orders_from_api()
    job_res = save_order_from_api(102, joblist)
    td = dt.datetime.today().date()
    tm = (dt.datetime.today() + dt.timedelta(days=1)).date()
    worker_res = []
    for x in [td.isoformat(), tm.isoformat()]:
        res = save_workers_from_api(x)
        worker_res.append(dict(date=x, res=res))
    return dict(job_res=job_res, worker_res=worker_res)


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


def create_dispatch(worker_summary, assigned_jobs, dispatch_date, deadline):
    city = "上海市"
    ws = worker_summary.reset_index()
    disps = []
    disp_sch = SchDispatch(city)

    for idx, row in ws.iterrows():
        #     print(row['worker_id'])
        orders = assigned_jobs[assigned_jobs.worker_id == row['worker_id']].loc[:, (
                                                                                       'addr', 'order_id', 'plan_start',
                                                                                       'plan_end')].sort_values(
            'plan_start')
        first_job_time = orders.iloc[0].plan_start
        # #: 派单日期和deadline 设置
        # if dispatch_date != dt.datetime.today().isoformat():
        #     disp_deadline = max(dt.datetime.strptime(
        #         dispatch_date + ' 20:00', "%Y-%m-%d %H:%M"), dt.datetime.today() + dt.timedelta(days=1)) + dt.timedelta(seconds=deadline)
        # else:
        #     disp_deadline = first_job_time - dt.timedelta(seconds=1800)
        # # dispatch_date = dispatch_date_t.strftime('%Y-%m-%d %H:%M:%S')
        # disp_deadline_str = dt.datetime.strftime(
        #     disp_deadline, "%Y-%m-%d %H:%M")
        orders.columns = ['addr', 'order_id', 'start_time', 'end_time']
        orders.start_time = orders.start_time.apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M'))
        orders.end_time = orders.end_time.apply(
            lambda x: x.strftime('%Y-%m-%d %H:%M'))
        order_list = list(orders.order_id)
        dispatch_info = dict(
            worker_id=row['worker_id'], orders=orders.to_dict('records'))
        disp_id = disp_sch.create(
            dispatch_date, row['worker_id'], deadline, dispatch_info, order_list)
        disp_data = dict(dispatch_info=dict(data=[dispatch_info]),
                         dispatch_date=dispatch_date, deadline=deadline)
        r = dispatch_to_api(disp_data, disp_id, disp_sch)
        if r == "success":
            disp_data.update(dispatch_id=disp_id)
            disps.append(disp_data)
        # disps.append(disp_data)  # 本地测试时，不调用 派单 api
    return disps


def sch_tomorrow():
    """
        派明天订单， 当前时间以后的
    """
    # 获取数据，更新到db
    process_unpaid_orders()
    r = save_data_from_api()
    city = "上海市"
    sch_datetime = dt.datetime.today().date() + dt.timedelta(days=1)
    # ：test data
    # sch_datetime = dt.datetime(2019, 4, 9, 11, 00)
    day_str = sch_datetime.isoformat()
    tm_datetime = dt.datetime.strptime(day_str, "%Y-%m-%d")
    sch_jobs = SchJobs(city)
    jobs = sch_jobs.unscheduled_jobs(tm_datetime)[:5]
    if jobs is None:
        return dict(status='error', msg='no jobs', data='')
    sch_workers = SchWorkers(city)
    workers = sch_workers.all_worker_by_date(day_str)
    if workers is None:
        return dict(status='error', msg='no workers', data='')
    # return "Done"
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
