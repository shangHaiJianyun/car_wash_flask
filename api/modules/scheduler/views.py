# -*- coding: utf-8 -*-
# from datetime import datetime
from statistics import _sum

from flask import jsonify, request

from api.modules.scheduler import sch_blu
from api.modules.scheduler.sch import *
from api.modules.scheduler.sch_lib import *
from api.modules.scheduler.sch_sim import *
from api.modules.scheduler.sch_api import *
import datetime


@sch_blu.route('/get_sim_data', methods=['POST'])
def gen_sim_data():
    '''
        生成 测试 的 worker 和 job 数据
    '''
    workday = request.json.get('workday')
    n_worker = request.json.get('n_worker')
    n_order = request.json.get('n_order')
    n_address = request.json.get('n_address')
    regions = request.json.get('regions')
    task_name = 'Sch test'
    city = u"上海市"
    sch_date = dt.datetime.strptime(workday, "%Y-%m-%d").date()

    #: gen simulate data
    workers = gen_worker(regions, workday, n_worker)
    jobs = gen_client_orders(regions, workday, n_order, n_address)

    #: save to db
    jobs.loc[:, 'status'] = 'open'
    jobs.loc[:, 'sch_date'] = sch_date
    # jobs = jobs.drop(['ts', 'hrs_t'], 1)

    s_jobs = SchJobs(city)
    j = s_jobs.df_insert(jobs)
    job_num = jobs.order_id.count()
    job_hrs = jobs.hrs.sum()
    sw = SchWorkers(city)
    worker_num = workers.worker_id.count()
    worker_hrs = np.sum(workers.w_hrs) - np.sum(workers.hrs_assigned)
    workers.loc[:, 'sch_date'] = sch_date

    sw.df_insert(workers)
    workers_db = sw.all_worker_by_date(workday)

    job_info = dict(
        job_num=int(job_num),
        job_hrs=float(job_hrs),
        worker_num=int(worker_num),
        worker_hrs=float(worker_hrs),
        sch_regions=regions
    )
    # s_task.update(new_task, job_info)
    # task_dtl = s_task.get(new_task)
    load_by_region = cal_city_loads_by_region(regions, jobs, workers)
    return jsonify(dict(
        status='success',
        job_info=job_info,
        # jobs=jobs.to_dict('records'),
        workers=workers_db.to_dict('records'),
        load_by_region=load_by_region,
    ))


@sch_blu.route('/sch_simulate', methods=['POST'])
def sch_simulate():
    """
        派单模拟
         1. simulate auto schedules

    """
    city = "上海市"
    sch_date = request.json.get('sch_date')
    res = start_multi_region_sch(city, sch_date)
    return jsonify(dict(status='ok', res=res))


@sch_blu.route('/sch_simulate_step2', methods=['POST'])
def sch_simulate_s2():
    """
        对未派单继续派单
         2. schedule_step2
    """
    # city = "上海市"
    sch_task = request.json.get('sch_task_id')
    res = schedule_step2(sch_task)
    return jsonify(dict(status='ok', res=res))


@sch_blu.route('/show_schedule_task', methods=['GET'])
def show_schedule_tasks():
    """
        Show open schedule tasks and subtasks
        input:
            city:

    """
    r = db.session.query(SchJobsM.sch_task_id, SchJobsM.sch_date, SchTaskM.sch_regions, SchJobsM.status, func.count(
        '*').label('job_counts')).group_by(SchJobsM.sch_task_id, SchJobsM.sch_date, SchTaskM.sch_regions,
                                           SchJobsM.status).all()
    tasks_l = [x._asdict() for x in r]
    tasks = []
    for t in tasks_l:
        if t['sch_task_id']:
            sub_task = SubTaskM.find(sch_task_id=t['sch_task_id']).all()
            t.update({'sub_task': [row2dict(x) for x in sub_task]})
        tasks.append(t)
    return jsonify(tasks)


@sch_blu.route('/reset_schedule_task', methods=['GET'])
def reset_job_task():
    """
        重置 job task， 在 schjobs table 里， 把 jobs 的 sch_task_id 设为 NUll， 以便重新测试派单
        input: 
            sch_task_id
        output:

    """
    sch_task_id = request.args.get('sch_task_id')
    q = SchJobsM.find(sch_task_id=sch_task_id)
    res = q.all()
    for x in res:
        x.sch_task_id = None
        x.worker_id = '0'
        db.session.flush()
        # order_list.append(row2dict(x))
    db.session.commit()
    q = SchJobsM.find(sch_task_id=sch_task_id).all()
    return jsonify('sch_task_id: %2d job resetted..' % len(res))


@sch_blu.route('/auto_schedule', methods=['GET', 'POST'])
def schedule_main():
    '''
        start schedule

    '''
    pass
    return jsonify(dict(task_info=''))


@sch_blu.route('/sch_result', methods=['GET', 'POST'])
def show_schedule_result():
    '''
        show schedule result
    '''
    # res = sch_jobs_today()
    res = sch_tomorrow()
    return jsonify(res)


@sch_blu.route('/sch_today', methods=['GET', 'POST'])
def show_schedule_result_today():
    '''
        show schedule result
    '''
    res = sch_jobs_today()
    # res = sch_tomorrow()
    return jsonify(res)


@sch_blu.route('/sch_get_data', methods=['GET', 'POST'])
def get_schedule_data_today():
    '''
        show schedule result
    '''
    res = save_data_from_api()

    #: schedule tomorrow
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
        # open_jobs.end_time = open_jobs.end_time.astype(str)
        # open_jobs.start_time = open_jobs.start_time.astype(str)
        open_jobs_dict = open_jobs.drop(['hrs_t'], 1).to_dict('records')

    else:
        open_jobs_dict = {}

    if assigned_jobs.empty:
        assigned_jobs = {}
    else:
        # assigned_jobs.end_time = assigned_jobs.end_time.astype(str)
        # assigned_jobs.start_time = assigned_jobs.start_time.astype(str)
        # assigned_jobs.plan_start = assigned_jobs.plan_start.astype(str)
        # assigned_jobs.plan_end = assigned_jobs.plan_end.astype(str)
        assigned_jobs_dict = assigned_jobs.drop(
            ['hrs_t'], 1).to_dict('records')
    return jsonify(dict(
        status='success',
        data=dict(
            assigned_jobs=assigned_jobs_dict,
            workers=arranged_workers.to_dict('records'),
            open_jobs=open_jobs_dict,
            worker_summary=worker_summary.to_dict('records'))
    ))


@sch_blu.route('/compare_worker_job', methods=['GET', 'POST'])
def compare_worker_job():
    """
    计算当天某一时间段订单数和技师数
    """
    # r = db.session.query(SchWorkersM.worker_id, SchWorkersM.w_start, SchWorkersM.w_hrs, SchWorkersM.bdt_hrs,
    #                      SchWorkersM.sch_date).all()
    # workers_l = [x._asdict() for x in r]
    # workers = []
    # for t in workers_l:
    #     if t['sch_date']:
    #         sch_jobs = SchJobsM.find(sch_date=t['sch_date']).all()
    #         t.update({'sch_job_hrs': [row2dict(x)['hrs'] for x in sch_jobs]})
    #     workers.append(t)
    # return jsonify(workers)
    today_time = datetime.date.today().isoformat()
    start_time = today_time + ' 06:00:00'
    end_time = today_time + ' 22:00:00'

    date_range = [x.strftime('%Y-%m-%d %H:%M:%S') for x in pd.date_range(start=start_time, end=end_time, freq='H')]
    # print(job_date)
    jobs = {}
    for index, value in enumerate(date_range):
        if index + 1 < len(date_range):
            next = date_range[index + 1]
        else:
            next = value
        q = SchJobsM.query.filter(and_(SchJobsM.start_time < str(next),
                                       SchJobsM.end_time >= str(value))).group_by(SchJobsM.start_time)
        jobs[value] = len(q.all())
    # w_start = today_time + ' 06:00:00'
    # w_end = today_time + ' 22:00:00'
    # worker_date = [x.strftime('%Y-%m-%d %H:%M:%S') for x in pd.date_range(start=start_time, end=end_time, freq='H')]
    # print(worker_date)
    workers = {}
    for index, value in enumerate(date_range):

        if index + 1 < len(date_range):
            next = date_range[index + 1]
        else:
            next = value
        r = SchWorkersM.query.filter(and_(SchWorkersM.w_start < str(next),
                                          SchWorkersM.w_end >= str(value))).group_by(SchWorkersM.w_start)
        workers[value] = len(r.all())
    # print(jobs, workers)
    return jsonify(dict(jobs_hrs=jobs, workers_hrs=workers))


@sch_blu.route('/load_by_region', methods=['GET', 'POST'])
def data_by_region():
    """
    获取该时间点的技师订单和区域
    """
    work_day = request.json.get('workday')
    city = '上海市'
    q = SchWorkersM.query.filter(
        and_(SchWorkersM.city == city, SchWorkersM.sch_date == work_day))

    worker_list = q.all()
    if worker_list:
        workers = [row2dict(x) for x in worker_list]
    else:
        workers = None

    # print(workers)
    sj = SchJobs(city)
    jobs = sj.jobs_by_date(work_day)
    # jobs = pd.DataFrame([x for x in orders])
    # print(jobs)
    if jobs:
        region_id = set([int(x['region_id']) for x in jobs])
        regions = list(region_id)
    else:
        regions = []
    # print(regions)
    # load_by_region = cal_city_loads_by_region(regions, jobs, workers)
    # print(load_by_region)
    return jsonify(dict(workers=workers, jobs=jobs, regions=regions))


@sch_blu.route('/data_by_region_date', methods=['GET', 'POST'])
def data_by_region_date():
    """
    根据指定的区域id和日期获取该时间点的技师和订单
    """
    work_day = request.json.get('workday')
    region_id = request.json.get('region_id')
    city = '上海市'
    workers = SchWorkersM.query.filter(
        and_(SchWorkersM.city == city, SchWorkersM.sch_date == work_day, SchWorkersM.w_region == region_id)).all()
    if workers:
        worker_list = [row2dict(x) for x in workers]
    else:
        worker_list = None

    # print(workers)
    jobs = SchJobsM.query.filter(
        and_(SchJobsM.city == city, SchJobsM.sch_date == work_day, SchJobsM.region_id == region_id)).all()

    if jobs:
        job_list = [row2dict(x) for x in jobs]
    else:
        job_list = []
    return jsonify(dict(worker_list=worker_list, job_list=job_list))
