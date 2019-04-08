# -*- coding: utf-8 -*-
# from datetime import datetime

from flask import jsonify, request

from api.modules.scheduler import sch_blu
from api.modules.scheduler.sch import *
from api.modules.scheduler.sch_lib import *
from api.modules.scheduler.sch_sim import *


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
    city = u"上海"
    sch_date = dt.datetime.strptime(workday, "%Y-%m-%d").date()

    #: gen simulate data
    workers = gen_worker(regions, workday, n_order)
    jobs = gen_client_orders(regions, workday, n_order, n_address)

    # arranged_workers = calculate_radt(jobs, workers)

    #: save to db
    s_task = SchTask(city)
    new_task = s_task.create(workday)
    # print(new_task, type(new_task))
    jobs.loc[:, 'sch_task_id'] = new_task
    jobs.loc[:, 'sch_status'] = 'pending'
    jobs = jobs.drop(['ts', 'hrs_t'], 1)
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
    # print(workers_db)
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
        status='success', jobs=jobs.to_dict('records'),
        workers=workers_db,
        load_by_region=load_by_region,
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


@sch_blu.route('/auto_schedule', methods=['POST'])
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
        print(x)
        sub_id = sub_task.create(task_id, x + task_id * 10000)
        sub_task_list.append(sch_task.get_sub(task_id))

    # create scheule job

    # get all jobs

    # get all availabe works

    # schedule step 1, 1st schedule by region

    # asign free worker with nearby open jobs

    # assign open jobs for swot team
    return jsonify(dict(task_info=task_info, sub_task_list=sub_task_list))


@sch_blu.route('/sch_result', methods=['POST'])
def show_schedule_result():
    '''
        show schedule result
    '''
    return
