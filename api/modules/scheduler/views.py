# -*- coding: utf-8 -*-
# from datetime import datetime

from flask import jsonify, request

from api.modules.scheduler import sch_blu
from api.modules.scheduler.sch import *
from api.modules.scheduler.sch_lib import *
from api.modules.scheduler.sch_sim import *
from api.modules.scheduler.sch_api import *


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
    workers = gen_worker(regions, workday, n_order)
    jobs = gen_client_orders(regions, workday, n_order, n_address)

    # arranged_workers = calculate_radt(jobs, workers)

    #: save to db
    s_task = SchTask(city)
    new_task = s_task.create(workday, task_name)
    # print(new_task, type(new_task))
    jobs.loc[:, 'sch_task_id'] = new_task

    jobs.loc[:, 'status'] = 'open'
    jobs.loc[:, 'sch_date'] = sch_date
    # jobs = jobs.drop(['ts', 'hrs_t'], 1)

    s_jobs = SchJobs(city)
    s_jobs.df_insert(jobs)
    job_num = jobs.order_id.count()
    job_hrs = jobs.hrs.sum()
    sw = SchWorkers(city)
    worker_num = workers.worker_id.count()
    worker_hrs = np.sum(workers.w_hrs) - np.sum(workers.hrs_assigned)
    workers.loc[:, 'sch_date'] = sch_date
    sw.df_insert(workers)
    workers_db = sw.all_worker_by_date(workday)
    # print('-----workdb_type----',type(workers_db))
    job_info = dict(job_num=int(job_num),
                    job_hrs=float(job_hrs),
                    worker_num=int(worker_num),
                    worker_hrs=float(worker_hrs),
                    sch_regions=regions
                    )

    s_task.update(new_task, job_info)
    task_dtl = s_task.get(new_task)

    load_by_region = cal_city_loads_by_region(regions, jobs, workers)

    return jsonify(dict(
        status='success',
        # jobs=jobs.to_dict('records'),
        # workers=workers_db.to_dict('records'),
        # load_by_region=load_by_region,
        sch_task=task_dtl
    ))


@sch_blu.route('/show_schedule_task', methods=['POST'])
def show_schedule_tasks():
    """
        Show open schedule tasks and subtasks
        input:
            city:

    """
    city = request.json.get('city')
    sch_task = SchTask(city)
    task_list = sch_task.list_all()
    tasks = []
    for x in task_list:
        sub_task = sch_task.get_sub(x['id'])
        tasks.append(dict(task=x, sub_task=sub_task))
    return jsonify(tasks)


@sch_blu.route('/auto_schedule', methods=['GET', 'POST'])
def schedule_main():
    '''
        start schedule

    '''
    city = request.json.get('city')
    task_id = request.json.get('task_id')
    sch_task = SchTask(city)
    task_info = sch_task.get(task_id)
    sub_task = SubTask(city)
    sub_task_list = []
    for x in task_info['sch_regions']:
        # print(x)
        sub_id = sub_task.create(task_id, x + task_id * 10000)
        sub_task_list.append(sch_task.get_sub(task_id))

    # create scheule job

    # get all jobs

    # get all availabe works

    # schedule step 1, 1st schedule by region

    # asign free worker with nearby open jobs

    # assign open jobs for swot team
    return jsonify(dict(task_info=task_info, sub_task_list=sub_task_list))


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


@sch_blu.route('/sch_test', methods=['GET', 'POST'])
def schedule_test():
    '''
        test multi region schedule
    '''
    #: get simulate data
    city = u'上海市'
    sch_task_id = request.json.get('sch_task_id')
    st = SchTask(city)
    task_info = st.get(sch_task_id)
    day_str = task_info['sch_date'].isoformat()
    # n_order = request.json.get('n_order')
    # n_worker = request.json.get('n_worker')
    # n_worker = request.json.get('n_address')
    # workday = request.json.get('workday')
    # jobs = gen_client_orders(regions, workday, n_order, n_address)
    # workers = gen_worker(regions, day_str, n_worker)

    #: get data from  db
    job_ = SchJobs(city)
    jobs_list = job_.jobs_by_sch_task(sch_task_id)
    jobs = pd.DataFrame(jobs_list)

    work_ = SchWorkers(city)
    workers = work_.all_worker_by_date(day_str)

    regions = task_info['sch_regions']
    #: 1st step schedule job by region
    for r in regions:
        r_jobs = jobs.loc[jobs.region_id == r]
        r_workers = workers
        if len(r_workers):
            assigned_jobs, open_jobs, worker_summary, arranged_workers = dispatch_region_jobs(
                r_jobs, r_workers, day_str)
            print('r', r)
            print(assigned_jobs)

    #: save result

    #: get all openjobs

    #: iter openjobs by region
    #:find nearby region
    #: asign job to nearby worker

    #: get remain jobs
    #: assign to sowt worker
    return
