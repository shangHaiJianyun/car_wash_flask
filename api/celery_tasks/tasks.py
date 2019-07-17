# -*- coding: utf-8 -*-
# # @Time    : 19-1-24 上午10:14
import json
import time
import datetime as dt
import requests


from api.celery_tasks import celery
# from api.modules.scheduler.sch_lib import *
from api.modules.scheduler.sch_api import sch_jobs_today, sch_tomorrow
from api.modules.scheduler.sch_api import set_order_paid
# from api.modules.scheduler.sch_api import sch_tomorrow_by_region


@celery.task
def sch_tomorrow_orders():
    sch_tomorrow()


@celery.task
def sch_today_orders():
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


#: region_job arrange
@celery.task(name="region_job_sch", bind=True)
def region_job_sch(self, task_id, region_id, city="上海市"):
    celery_uid = self.request.id
    # sch_tomorrow_by_region(task_id, region_id, celery_uid, city="上海市")
    return celery_uid
