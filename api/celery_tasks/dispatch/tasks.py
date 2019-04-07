# -*- coding: utf-8 -*-
# # @Time    : 19-1-24 上午10:14
#
from flask import current_app
from celery.utils.log import get_task_logger
import celery
logger = get_task_logger(__name__)


@celery.task
def dispatch():
    # logger.info()
    print('celery...')


#
# # 在api中调用时使用 dispatch.delay(对应参数)
