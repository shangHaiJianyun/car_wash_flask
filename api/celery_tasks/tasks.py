# -*- coding: utf-8 -*-
# # @Time    : 19-1-24 上午10:14
import json
import time
import datetime as dt
import requests


from api.celery_tasks import celery
# from api.modules.scheduler.sch_lib import *
from api.modules.scheduler.sch_api import sch_jobs_today
from api.modules.scheduler.sch_api import set_order_paid


@celery.task
def sch_order():
    sch_jobs_today()


@celery.task
def change_order_status():
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
    paid_id = []
    for x in data:
        order_ids = x["order_id"]
        res = set_order_paid(order_ids)
        if res:
            paid_id.append(order_ids)
    return paid_id
