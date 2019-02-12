# -*- coding: utf-8 -*-
# # @Time    : 19-1-24 上午10:14
#
# from flask import current_app
# from celery.utils.log import get_task_logger
# from api import celery
# logger = get_task_logger(__name__)
#
#
# @celery.task
# def dispatch():
#     logger.info()
#     pass
#
#
# # 在api中调用时使用 dispatch.delay(对应参数)
