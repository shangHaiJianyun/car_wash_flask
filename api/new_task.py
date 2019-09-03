import json
import datetime as dt
import requests

from celery.utils.log import get_task_logger

from api import make_celery, create_app
from api.modules.scheduler.sch_sim import start_multi_region_sch
from api.modules.scheduler.sch_api import set_order_paid
from api.modules.scheduler.sch_sim import sch_tomorrow_by_region

logger = get_task_logger(__name__)

celery = make_celery(create_app('dev'))


@celery.task(name="region_job_sch", bind=True)
def region_job_sch(self, task_id, region_id, sch_date_str):
    celery_uid = self.request.id
    sch_tomorrow_by_region(task_id, region_id, celery_uid, sch_date_str, city="上海市")
    return celery_uid


@celery.task(name='sch_today_jobs')
def sch_today_jobs():
    city = "上海市"
    sch_date = dt.datetime.today().date().isoformat()
    res = start_multi_region_sch(city, sch_date)
    return res


@celery.task(name='sch_tomorrow_jobs')
def sch_today_jobs():
    city = "上海市"
    sch_date = dt.date.today()
    tomorrow = sch_date + dt.timedelta(days=1)
    tomorrow_date = str(tomorrow.strftime('%Y-%m-%d'))
    res = start_multi_region_sch(city, tomorrow_date)
    return res


@celery.task(name='change_status')
def change_order_status():
    access_key = 'xunjiepf'
    url = "https://xcx.upctech.com.cn/api/extend/getorderlist"
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
