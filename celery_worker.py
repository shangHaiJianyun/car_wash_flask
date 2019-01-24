# -*- coding: utf-8 -*-
# @Time    : 19-1-24 上午10:19

from api import create_app,celery


app = create_app('dev')
app.app_context().push()
