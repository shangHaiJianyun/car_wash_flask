# -*- coding: utf-8 -*-
import math
import datetime as dt
import time
import random
import json
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import *
# from flask import current_app as app
from api.models.models import *
from .sch_model import *
from config import *

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)


class SchTask():
    def __init__(self, city):
        self.city = city

    def create(self, sch_date_str):
        sch_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d")
        new_sch = SchTaskM(city=self.city, sch_date=sch_date)
        db.session.add(new_sch)
        db.session.commit()
        return new_sch.id

    def get(self, task_id):
        print(task_id, type(task_id))
        res = SchTaskM.query.filter(SchTaskM.id == task_id).one_or_none()
        return row2dict(res)

    def list_all(self):
        res = SchTaskM.query.all()
        return [row2dict(x) for x in res]

    def get_by_date(self, sch_date_str):
        sch_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d")
        res = SchTaskM.query.filter(
            and_(SchTaskM.city == self.city, SchTaskM.sch_date == sch_date)).all()
        if res:
            return [row2dict(x) for x in res]

    def update(self, task_id, args):
        sch_task = SchTaskM.query.filter(SchTaskM.id == task_id).update(args)
        db.session.commit()
        return self.get(sch_task)

    def get_sub(self, task_id):
        subs = SubTaskM.query.filter(SubTaskM.sch_task_id == task_id).all()
        if subs:
            return [row2dict(x) for x in subs]
        else:
            return None


class SubTask():
    def __init__(self, city):
        self.city = city

    def get(self, id):
        res = SubTaskM.query.filter(SubTaskM.id == id).one_or_none()
        return row2dict(res)

    def create(self, task_id, sub_task_uid):
        sub_id = SubTaskM.query.filter(
            and_(sub_task_uid == sub_task_uid)).one_or_none()
        if sub_id:
            return self.get(sub_id.id)
        else:
            new_sub = SubTaskM(sch_task_id=task_id,
                               sub_task_uid=sub_task_uid, city=self.city)
            db.session.add(new_sub)
            db.session.commit()
            return self.get(new_sub.id)

    def update(self, id, **args):
        sub_task = SubTaskM.query.filter(SubTaskM.id == id).update(args)
        return self.get(sub_task.id)

    def get_by_date(self, sch_date_str):
        job_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d").date()
        res = SubTaskM.query.filter(
            and_(SubTaskM.sch_date == sch_date, SubTaskM.city == self.city)).all()

    def get_by_uid(self, uid):
        sub_task = SubTaskM.query.filter(and_(
            SubTaskM.sub_task_uid == uid, SubTaskM.city == self.city)).one_or_none()
        return row2dict(sub_task)


class SchJobs():
    def __init__(self, city):
        self.city = city
        self.engine = engine

    def unscheduled_jobs(self, city):
        '''
            get un_scheduled jobs from php database and insert to sch_jobs
        '''
        pass

    def jobs_by_date(self, sch_date_str):
        job_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d").date()
        res = SchJobsM.query.filter(and_(
            SchJobsM.job_date == job_date, SchJobsM.city == self.city)).all()
        if res:
            return [row2dict(x) for x in res]

    def jobs_by_sch_task(self, task_id):
        res = SchJobsM.query.filter(and_(
            SchJobsM.sch_task_id == task_id, SchJobsM.city == self.city)).all()
        if res:
            return [row2dict(x) for x in res]

    def df_insert(self, df):
        try:
            df.to_sql('sch_jobs', self.engine, if_exists='append',
                      index=False, chunksize=1000)
            return True
        except Exception as err:
            return False

    def df_update(self, df):
        to_update = df.to_dict('records')
        try:
            for x in to_update:
                SchJobsM.query.filter(SchJobsM.id == x['id']).update(x)
                db.session.flush()
            db.session.commit()
            return True
        except:
            return False


class SchWorkers():
    def __init__(self, city):
        self.city = city
        self.engine = engine

    def workers_from_php(self, sch_date_str):
        '''
            get job from php
        '''
        pass

    def df_insert(self, df):
        try:
            df.to_sql('sch_workers', self.engine, if_exists='append',
                      index=False, chunksize=1000)
            return True
        except Exception as err:
            print('insert worker...', err)
            return False

    def df_update(self, df):
        to_update = df.to_dict('records')
        try:
            for x in to_update:
                SchWorkersM.query.filter(SchWorkersM.id == x['id']).update(x)
                db.session.flush()
            db.session.commit()
            return True
        except:
            return False

    def all_worker_by_date(self, sch_date_str):
        sch_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d").date()

        workers = SchWorkersM.query.filter(
            and_(SchWorkersM.city == self.city, SchWorkersM.sch_date == sch_date)).all()
        if workers:
            return [row2dict(x) for x in workers]
        else:
            return None

    def get_worker_info_by_date(self, worker_id, sch_date_str):
        sch_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d").date()
        worker_info = SchWorkersM.query.filter(
            and_(SchWorkersM.worker_id == worker_id, SchWorkersM.sch_date == sch_date)).one_or_none()
        if worker_info:
            return row2dict(worker_info)
        else:
            return None

    def get_worker_jobs(self, worker_id, sch_date_str):
        '''
            worker's assigned jobs by date
        '''
        job_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d").date()
        w_jobs = SchJobsM.query.filter(and_(
            SchJobsM.city == self.city, SchJobsM.wrk_id == worker_id, SchJobsM.job_date == job_date)).all()
        if w_jobs:
            return [row2dict(x) for x in w_jobs]
        else:
            return None

    def get_worker_free_time(self, worker_id, sch_date_str):
        '''
            worker's free time
        '''
        sch_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d").date()
        work_info = self.get_worker_info_by_date(worker_id, sch_date_str)
        free_time = []

        if work_info:
            w_start = worker_info.w_start
            w_end = worker_info.w_end
            worker_jobs = self.get_worker_jobs(worker_id, sch_date_str)
            if worker_jobs:
                df_jobs = pd.DataFrame(worker_jobs).sort_values(['plan_start'])
                df_jobs.loc[:, 'last_end'] = df_jobs.plan_end.shift(1)
                df_jobs.loc[:, 'spare_time'] = (
                    df_jobs.plan_start - df_jobs.last_end) / np.timedelta64(1, 'm')
                j_start = df_jobs.iloc[0].plan_start
                j_end = df_jobs.iloc[-1].plan_end

                if (j_start - w_start) / np.timedelta64(1, 'm') >= 60:
                    free_time.append(dict(w_start=w_start, w_end=j_start))

                spare_time = df_jobs[df_jobs.spare_time > 60]
                if len(spare_time) > 0:
                    for idx, row in spare_time.iterrows():
                        free_time.append(
                            dict(w_start=row.last_end, w_end=row.plan_start))

                if (w_end - j_end) / np.timedelta64(1, 'm') >= 60:
                    free_time.append(dict(w_start=j_end, w_end=w_end))
            else:
                free_time.append({'w_start': w_start, 'w_end': w_end})
        if len(free_time) > 0:
            return free_time
        else:
            return None

    def update_worker_info(self, worker_id, sch_date_str, worker_data):
        '''
            update worker info
        '''
        sch_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d").date()
        try:
            SchWorkersM.query.filter(and_(
                SchWorkersM.worker_id == worker_id, SchWorkersM.sch_date == sch_date)).update(data)
            db.session.commit()
            return self.get_worker_info_by_date(worker_id, sch_date_str)
        except:
            return None


class SchDispatch():
    def __init__(self, city):
        self.city = city

    def get(self, id):
        dispatch = SchDispatchM.query.filter(
            SchDispatchM.id == id).one_or_none()
        if dispatch:
            return row2dict(dispatch)

    def create(self, sch_date_str, worker_id, status):
        sch_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d")
        new_d = SchDispatchM(city=self.city, sch_date=sch_date,
                             worker_id=worker_id, status=status)
        db.session.add(new_d)
        db.session.commit()
        return self.get(new_d.id)

    def update(self, id, status):
        SchDispatchM.query.filter(SchDispatchM.id == id).update(status=status)
        db.session.commit()
        return self.get(id)

    def reject_dispatch(self, id):
        # remove job dispatch id, worker_id
        # update worker info
        pass

    def get_all_by_date(self, sch_date_str):
        sch_date = dt.datetime.strptime(sch_date_str, "%Y-%m-%d")
        d = SchDispatchM.query.filter(
            and_(SchDispatchM.sch_date == sch_date, SchDispatchM.city == self.city)).all()
        if d:
            return [row2dict(x) for x in d]
        else:
            return None

    def get_dispatch_jobs(self, id):
        pass

    def get_by_worker_id(self, worker_id):
        pass

    def get_by_worker_sch_day(self, worker_id, sch_date):
        pass


class SchTestLog():
    def create(self, log_type, log_data):
        nl = Sch_Test_Log(log_type=log_type, log_data=log_data)
        db.session.add(nl)
        db.session.commit()
        return nl.id

    def get_by_type(self, log_type):
        data = Sch_Test_Log.query.filter(Sch_Test_Log.log_type == log_type).order_by(
            Sch_Test_Log.created_on.desc()).all()
        if data:
            return [row2dict(x) for x in data]
