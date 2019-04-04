# -*- coding: utf-8 -*-
# from datetime import datetime
import json
import requests
import time
import random
import math
import numpy as np
import pandas as pd

from flask import jsonify, request

from api.modules.scheduler import sch_blu
from api.modules.scheduler.sch import *
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
    workers = get_worker(regions, workday, n_order)
    jobs = get_client_orders(regions, workday, n_order, n_address)
    arranged_workers = calculate_radt(jobs, workers)

    jobs = jobs.drop(['ts', 'hrs_t'], 1)
    load_by_region = cal_city_loads_by_region(regions, jobs, workers)
    return jsonify(dict(status='success', jobs=jobs.to_dict('records'), workers=workers.to_dict('records'), load_by_region=load_by_region, arranged_workers=arranged_workers.reset_index().to_dict('records')))


@sch_blu.route('/auto_schedule', methods=['POST'])
def schedule_main():
    '''
        start schedule
    '''
    return


@sch_blu.route('/sch_result', methods=['POST'])
def show_schedule_result():
    '''
        show schedule result
    '''
    return
