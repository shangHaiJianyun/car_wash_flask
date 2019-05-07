# -*- coding: utf-8 -*-
# # @Time    : 19-1-24 上午10:14
#
# import random
# import time
#
# from flask import current_app
import json
import time
import datetime as dt
import requests


from api.celery_tasks import celery
# from api.modules.scheduler.sch_lib import *
# from api.modules.scheduler.sch_api import *
from api.modules.scheduler.sch_api import set_order_paid


# @celery.task
# def set_order_to_paid():
#     """
#         定时将 新订单设置为付款，每次将 page 1 的订单设为 已付款
#     """
#     res = process_unpaid_orders()
#     return res
#
# @celery.task
# def sch_order():
#     sch_jobs_today()
#
# @celery.task
# def get_order():
#     access_key = 'xunjiepf'
#
#     results = requests.post(
#         url="https://banana.xunjiepf.cn/api/extend/getorderlist",
#         params={
#             'access_key': access_key
#         }
#     )
#     page_size = results.json()['data']['total_count']
#
#     res = requests.post(
#         url="https://banana.xunjiepf.cn/api/extend/getorderlist",
#         headers={
#             "Content-Type": "application/json"
#         },
#         data=json.dumps({
#             'access_key': access_key,
#             'page_size': page_size,
#             "order_status": 2,
#             "start_service_date": "2019-04-8",
#             "end_service_date": "2019-04-15"
#
#         })
#     )
#     result = res.json()['data']['data']
#     return result


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
