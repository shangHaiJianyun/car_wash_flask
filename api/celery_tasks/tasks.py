# -*- coding: utf-8 -*-
# # @Time    : 19-1-24 上午10:14
#
# import random
# import time
#
# from flask import current_app

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
