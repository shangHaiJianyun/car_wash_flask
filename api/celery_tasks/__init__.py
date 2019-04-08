# -*- coding: utf-8 -*-
# @Time    : 19-1-24 上午10:00


"""
1.配置celery
2.定义异步任务
3.装饰器装饰所用位置
4.在终端运行
celery worker -A api.celery_tasks.tasks --loglevel=info
celery -A api.celery_tasks.tasks:celery worker -l info -B (定时)

"""
from celery.utils.log import get_task_logger

from api import make_celery, create_app

logger = get_task_logger(__name__)

celery = make_celery(create_app('dev'))