# -*- coding: utf-8 -*-
import json

import datetime as dt
from flask_sqlalchemy import SQLAlchemy
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
# from flask import current_app
from sqlalchemy import JSON
from api.models.models import db

# db = SQLAlchemy()


class SchTaskM(db.Model):
    # __bind_key__ = 'sch'
    __tablename__ = 'sch_tasks'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(32), index=True,)
    name = db.Column(db.String(32))
    sch_date = db.Column(db.Date, index=True)
    sch_regions = db.Column(JSON())
    job_num = db.Column(db.Integer)
    job_hrs = db.Column(db.Float)
    worker_num = db.Column(db.Integer)
    worker_hrs = db.Column(db.Float)
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String(10), index=True, )


class SubTaskM(db.Model):
    # __bind_key__ = 'sch'
    """
        区域派单子任务
    """
    __tablename__ = 'sub_tasks'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(32))
    sch_task_id = db.Column(db.Integer, index=True,)
    sub_task_uid = db.Column(db.String(32), index=True,)
    sch_date = db.Column(db.DateTime)
    status = db.Column(db.String(10))
    region_id = db.Column(db.String(10))
    job_num = db.Column(db.Integer)
    job_hrs = db.Column(db.Float)
    worker_num = db.Column(db.Integer)
    worker_hrs = db.Column(db.Float)
    open_job_num = db.Column(db.Integer)
    open_job_hrs = db.Column(db.Float)
    open_worker_num = db.Column(db.Integer)
    open_worker_hrs = db.Column(db.Float)
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())
    modified_on = db.Column(db.DateTime, default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())


class SchWorkersM(db.Model):
    __tablename__ = 'sch_workers'
    id = db.Column(db.Integer, primary_key=True)
    # sch_task_id = db.Column(db.Integer)
    city = db.Column(db.String(32), index=True)
    worker_id = db.Column(db.String(10), index=True)
    w_region = db.Column(db.String(10), index=True)
    sch_date = db.Column(db.String(20), index=True)
    w_type = db.Column(db.String(20))
    worker_type = db.Column(db.Integer, index=True)
    w_hrs = db.Column(db.Float)
    w_rank = db.Column(db.Integer, index=True)
    max_star_t = db.Column(db.Float)
    mdt = db.Column(db.Float)
    bdt_hrs = db.Column(db.Float)
    adt_hrs = db.Column(db.Float)
    min_hrs = db.Column(db.Float)
    hrs_assigned = db.Column(db.Float)
    hrs_to_assign = db.Column(db.Float)
    w_start = db.Column(db.String(20))
    w_end = db.Column(db.String(20))


class SchJobsM(db.Model):
    __tablename__ = 'sch_jobs'
    id = db.Column(db.Integer, primary_key=True)
    sch_task_id = db.Column(db.Integer, index=True)
    city = db.Column(db.String(32), index=True)
    region_id = db.Column(db.String(10), index=True)
    addr = db.Column(db.String(10))
    sch_date = db.Column(db.String(20), index=True)
    order_id = db.Column(db.String(20))
    job_type = db.Column(db.String(10))
    start_time = db.Column(db.String(20))
    end_time = db.Column(db.String(20))
    plan_start = db.Column(db.String(20))
    plan_end = db.Column(db.String(20))
    hrs = db.Column(db.Float)
    worker_id = db.Column(db.String(10), index=True, default='0')
    sch_task_id = db.Column(db.Integer, index=True)
    status = db.Column(db.String(20), index=True, )
    dispatch_id = db.Column(db.Integer, index=True)


class SchDispatchM(db.Model):
    """
        Dispatch by Worker
    """
    __tablename__ = 'sch_dispatch'
    id = db.Column(db.Integer, primary_key=True)
    sch_task_id = db.Column(db.Integer, index=True)
    city = db.Column(db.String(32), index=True)
    sch_date = db.Column(db.String(20), index=True)
    dispatch_date = db.Column(db.String(20), index=True)
    deadline = db.Column(db.Integer)
    dispatch_info = db.Column(JSON())
    worker_id = db.Column(db.Integer, index=True)
    status = db.Column(db.String(20), index=True, )
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())


class Sch_Test_Log(db.Model):
    __tablename__ = 'sch_test_log'
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(50), index=True)
    log_data = db.Column(JSON())
    created_on = db.Column(db.DateTime, default=db.func.current_timestamp())
