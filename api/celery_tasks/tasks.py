# -*- coding: utf-8 -*-
# # @Time    : 19-1-24 上午10:14
#
# import random
# import time
#
# from flask import current_app
import json

import requests

from api.celery_tasks import celery


@celery.task
def dispatch():
    # logger.info()
    # print('celery...')
    pass


@celery.task
def get_order():
    access_key = 'xunjiepf'

    results = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getorderlist",
        params={
            'access_key': access_key
        }
    )
    page_size = results.json()['data']['total_count']

    res = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getorderlist",
        headers={
            "Content-Type": "application/json"
        },
        data=json.dumps({
            'access_key': access_key,
            'page_size': page_size,
            "order_status": 2,
            "start_service_date": "2019-04-8",
            "end_service_date": "2019-04-15"

        })
    )
    result = res.json()['data']['data']
    return result
