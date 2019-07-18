import json
import requests

from celery.utils.log import get_task_logger

from api import make_celery, create_app
from api.modules.scheduler import set_order_paid
from api.modules.scheduler.sim_sch_api import sch_tomorrow_by_region

logger = get_task_logger(__name__)

celery = make_celery(create_app('dev'))


@celery.task(name="region_job_sch", bind=True)
def region_job_sch(self, task_id, region_id):
    celery_uid = self.request.id
    sch_tomorrow_by_region(task_id, region_id, celery_uid, city="上海市")
    return celery_uid


@celery.task(name='change_status')
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
