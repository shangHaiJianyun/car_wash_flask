# -*- coding: utf-8 -*-
import json
import time
import datetime as dt
import requests

from api.celery_tasks import celery


# from api.celery_tasks.dispatch import region_job_sch
@celery.task(name="region_job_sch", bind=True)
def region_job_sch(self, task_id, region_id, city="上海市"):
    celery_uid = self.request.id
    # sch_tomorrow_by_region(task_id, region_id, celery_uid, city="上海市")
    return celery_uid
