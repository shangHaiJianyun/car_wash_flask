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


# @celery.task(bind=True)
# def long_task(self):
#     total = random.randint(10, 50)
#     for i in range(total):
#         self.update_state(state=u'处理中', meta={'current': i, 'total': total})
#         time.sleep(1)
#     return {'current': 100, 'total': 100, 'result': u'完成'}

#
# # 在api中调用时使用 dispatch.delay(对应参数)

@celery.task
def get_order(order_status,start_service_date,end_service_date):
    access_key = 'xunjiepf'
    results = requests.post(
        url="https://banana.xunjiepf.cn/api/extend/getorderlist",
        params={
            'access_key': access_key
        }
    )
    page_size = results.json()['data']['total_count']
    if order_status and start_service_date and end_service_date:
        res = requests.post(
            url="https://banana.xunjiepf.cn/api/extend/getorderlist",
            headers={
                "Content-Type": "application/json"
            },
            data=json.dumps({
                'access_key': access_key,
                'page_size': page_size,
                'order_status': order_status,
                'start_service_date': start_service_date,
                'end_service_date': end_service_date
            })
        )
    else:
        res = requests.post(
            url="https://banana.xunjiepf.cn/api/extend/getorderlist",
            params={
                'access_key': access_key,
                'page_size': page_size,
            }
        )
    result = res.json()['data']['data']
    return result
