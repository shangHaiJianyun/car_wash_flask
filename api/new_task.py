import json
import time
import datetime as dt
import requests


from celery.utils.log import get_task_logger

from api import make_celery, create_app
from api.modules.scheduler.sim_sch_api import sch_tomorrow_by_region

logger = get_task_logger(__name__)

celery = make_celery(create_app('dev'))


@celery.task(name="region_job_sch", bind=True)
def region_job_sch(self, task_id, region_id):
    celery_uid = self.request.id
    sch_tomorrow_by_region(task_id, region_id, celery_uid, city="上海市")
    return celery_uid
