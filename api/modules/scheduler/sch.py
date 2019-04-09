# -*- coding: utf-8 -*-
import math
import datetime
import datetime as dt
import time
import random
import json
import numpy as np
import pandas as pd

# from api.models.models import *
from api.modules.scheduler.sch_lib import *

# ：区域工时 供需计算


def cal_region_order_req(region_jobs, period, bucket='start_time'):
    '''
        按 period 计算需求工时
        bucket: 'start_time' 或 'plan_start'
    '''
    d = region_jobs.iloc[0].start_time.date().isoformat()
    period = '1h'
    hrs_idx = pd.date_range(d + ' 6:00', d + ' 22:00', freq=period)
    region_all = pd.DataFrame()
    for idx, row in region_jobs.iterrows():
        job_idx = pd.date_range(row.start_time, row.end_time, freq='1h')
        job_bucket = pd.DataFrame(
            columns=['addr', 'order_hrs'], index=job_idx).fillna(0)
        job_bucket.loc[:, 'req_hrs'] = row.hrs / len(job_idx)
        job_bucket.loc[:, 'addr'] = row.addr
    #     hrs_bucket = hrs_idx.join(hrs_bucket).fillna(0)
        region_all = region_all.append(job_bucket)
    region_sum = region_all.resample(period).agg({
        'req_hrs': 'sum'
    })
    return region_sum


def cal_region_wrk_hrs(region_wkrs, period='1h'):
    '''
        计算区域工人工时
    '''
    d = region_wkrs.iloc[0].w_start.date().isoformat()
    hrs_idx = pd.date_range(d + ' 6:00', d + ' 22:00', freq=period)
    hrs_bucket = pd.DataFrame(
        columns=['wrks', 'wrk_hrs'], index=hrs_idx).fillna(0)
    for idx, row in region_wkrs.iterrows():
        wh_idx = pd.date_range(row.w_start, row.w_end, freq='1h')
        w_bucket = pd.DataFrame(
            columns=['wrks', 'wrk_hrs'], index=wh_idx).fillna(1)
        hrs_bucket = hrs_bucket.join(w_bucket, rsuffix='_').fillna(0)
        hrs_bucket.loc[:, 'wrks'] = hrs_bucket.wrks + hrs_bucket.wrks_
        hrs_bucket.loc[:, 'wrk_hrs'] = hrs_bucket.wrk_hrs + hrs_bucket.wrk_hrs_
        hrs_bucket = hrs_bucket.drop(['wrks_', 'wrk_hrs_'], 1)
    hrs_bucket = hrs_bucket.resample(period).agg(
        {'wrks': 'mean', 'wrk_hrs': 'sum'})
    return hrs_bucket


def calculate_region_loads(region_id, jobs, workers, period, bucket='start_time'):
    '''
        计算区域工时供求
    '''
    region_req = cal_region_order_req(jobs, period, bucket)
    region_wrk_hrs = cal_region_wrk_hrs(workers, period)
#     region_req_supply = region_req.join(region_wrk_hrs).fillna(0)
    region_req_supply = region_wrk_hrs.join(region_req).fillna(0)
    region_req_supply.loc[:, 'region_id'] = region_id
    region_req_supply.loc[:, 'short_hrs'] = region_req_supply.wrk_hrs - \
        region_req_supply.req_hrs
    return region_req_supply


def cal_city_loads_by_region(regions, jobs, workers):
    period = '1h'
    load_by_region = []
    for region_id in regions:
        region_jobs = jobs[jobs.region_id == region_id]
        region_wrk = workers[workers.w_region == region_id]
        region_req_supply = calculate_region_loads(
            region_id, region_jobs, region_wrk, period)
        # region_req_supply.loc[:, ('req_hrs', 'wrk_hrs')].plot.bar()
        # plt.show()
        load_by_region.append(
            dict(region=region_id, data=region_req_supply.reset_index().to_dict('records')))
    return load_by_region


#:  技师 radt 排序
def calculate_radt(region_jobs, region_workers):
    region_workers = region_workers[region_workers.worker_type != 3]  # : 不考虑特服
    # 当日技师必派单 总量
    total_wrk_bdt = region_workers.loc[region_workers.mdt > 0].sum().bdt_hrs
    total_wrk_min_hrs = region_workers.sum().min_hrs  # 技师 adt
    total_wrk_available_hrs = region_workers.sum().w_hrs   # 技师可用工时
    mdt_total = region_workers.sum().mdt

    # 当日订单总量
    total_req_hrs = region_jobs.sum().hrs
    # print('Total, req hrs %2.2f , total 必派单 hrs %2.2f, total min hrs %2.2f,total wrk hrs %2.2f ' % (
    #     total_req_hrs, total_wrk_bdt, total_wrk_min_hrs, total_wrk_available_hrs))

    radt = total_req_hrs - total_wrk_min_hrs
    if radt > 0:
        #         # Adt，Bdt，P由大到小排序Adt1…Adt
        region_workers.loc[:, 'adt_hrs'] = region_workers.min_hrs
        region_workers = region_workers.sort_values(
            ['adt_hrs', 'bdt_hrs', 'w_rank'], ascending=[0, 0, 0])
        # print('radt  需求工时 %2.2f > 必派单技师需求量 %2.2f' % (total_req_hrs, total_wrk_min_hrs))
    else:
        #:         If Mdt> Min(Mat,Mst),
        #:         Adt=Bdt=Min(Mat,Mst)
        #:         If Mdt<=Min(Mat,Mst), Bdt=Mdt
        #:         Adt=Bdt+{Addt-Sum(Bdt)}*{Min(Mat,Mst)-Bdt}/Sum{Min(Mat,Mst)-Bdt
        total_bdt = region_workers.bdt_hrs.sum()
        temp = region_workers.min_hrs.sum() - region_workers.bdt_hrs.sum()
        if temp == 0:
            adt_adj = 0
        else:
            region_workers.loc[:, 'bdt_hrs'] = np.where(
                region_workers.mdt < region_workers.min_hrs, region_workers.mdt, region_workers.bdt_hrs)
            adt_adj = (total_req_hrs - total_bdt) * \
                (region_workers.min_hrs - region_workers.bdt_hrs) / temp
#         region_workers.loc[:, 'adt_hrs'] = np.where((region_workers.bdt_hrs + adt_adj) > 0, region_workers.bdt_hrs + adt_adj, 0)
        region_workers.loc[:, 'adt_hrs'] = region_workers.bdt_hrs + adt_adj

        region_workers = region_workers.sort_values(
            ['bdt_hrs', 'adt_hrs', 'w_rank', 'worker_type', ], ascending=[0, 0, 0, 1])
        # print('radt  需求工时 %2.2f < 必派单技师需求量 %2.2f, bdt total %2.2f' % (total_req_hrs, total_wrk_min_hrs, total_bdt))
#         print(adt_adj)
#         print(region_workers)
    return region_workers


def sort_jobs(jobs, order_interval, w_start, w_end):
    '''
        订单排序
    '''
    max_wait_interval = datetime.timedelta(seconds=7200)

    jobs.loc[:, 'late_start'] = jobs.end_time + jobs.hrs_t
    jobs = jobs.sort_values(['addr', 'start_time', 'late_start'], ascending=[
                            1, 1, 1]).reset_index().drop(['index'], 1)
    jobs.loc[:, 'trans_hr'] = 0
#     total_orders_addr = job2.groupby('addr').agg({'order_id': 'count'})
#     print('按地址统计订单数')
#     print(total_orders_addr)
    addrs = np.unique(np.array(jobs.addr))
#     addrs = total_orders_addr.index
    job_sorted = pd.DataFrame()
    k = 1
    for addr in addrs:
        job3 = jobs.loc[jobs.addr == addr]
        job3.loc[:, 'grp'] = 0
#         job3.loc[:, 'total_orders'] = total_orders_addr.loc[addr, 'order_id']
        while len(job3) > 0:
            first_idx = job3.index[0]
            plan_start = w_start
            plan_end = job3.iloc[0].hrs_t + plan_start
            # job3.loc[:, 'plan_start'] = job3.start_time.shift(1) + job3.hrs_t.shift(1)
            # job3.loc[:, 'plan_end'] = job3.plan_start + job3.hrs_t
            job3.loc[first_idx, 'plan_start'] = plan_start
            job3.loc[first_idx, 'plan_end'] = plan_end
            job3.loc[first_idx, 'grp'] = k

            job_sorted = job_sorted.append(job3.iloc[0])

            job3 = job3.drop([first_idx])
            for t, row in job3.iterrows():
                #                 print('t ..', t,  'grp ', k, 'order_id', job3.loc[t, 'order_id'])
                job3.loc[t, 'grp'] = k
                if (plan_end + row.hrs_t + order_interval < row.end_time) & (plan_end + max_wait_interval > row.start_time):
                    row.grp = k
                    if row.start_time >= plan_end + order_interval:
                        row.plan_start = row.start_time
                        row.plan_end = row.start_time + row.hrs_t
                        plan_end = row.plan_end
                        job_sorted = job_sorted.append(row)
                    else:
                        row.plan_start = plan_end + order_interval
                        row.plan_end = row.plan_start + row.hrs_t + order_interval
                        row.trans_hr = order_interval.seconds / 3600
                        plan_end = row.plan_end
                        job_sorted = job_sorted.append(row)
                    job3 = job3.drop([t])
            k = k+1
    job_sorted = job_sorted.astype(
        {'addr': int, 'grp': int, 'job_type': int, 'order_id': int})
    job_sorted = job_sorted.loc[job_sorted.plan_start.notnull(), ('addr', 'grp', 'job_type', 'order_id',
                                                                  'start_time', 'plan_start', 'plan_end', 'end_time', 'hrs', 'hrs_t', 'trans_hr')]
    job_sorted = job_sorted.loc[job_sorted.plan_end <= w_end]
    job_sorted = job_sorted.loc[job_sorted.plan_start.notnull()]
    job_sorted.set_index(['addr', 'grp']).sort_values(
        ['addr', 'grp', 'plan_start'])
    job_sorted.loc[:, 'wait_hr'] = np.where(job_sorted.grp.shift(1) == job_sorted.grp,
                                            (job_sorted.plan_start - job_sorted.plan_end.shift(1))/np.timedelta64(1, 'h') - job_sorted.trans_hr, 0)

    return job_sorted


def dispatch_region_jobs(jobs, workers, day_str):
    '''
        派单
        input:
                jobs
                workers
        output:
                assigned_jobs
                open_jobs
                worker_summary
                arranged_workers

    '''
    #: 订单

    assigned_jobs = pd.DataFrame()
    order_interval = dt.timedelta(seconds=300)
    jobs_by_addr = jobs.groupby(['addr']).agg({
        'addr': 'last',
        'hrs': 'sum',
        'order_id': 'count'}).sort_values(['hrs'], ascending=[0])
#     print(jobs_by_addr)
    jobs.loc[:, 'worker_id'] = 0
#     print(jobs.head())
    # ：技师排序
    arranged_workers = calculate_radt(jobs, workers)
    sch_workers = SchWorkers(city="上海市")
    # print('start .... %2d workers to assign' % len(arranged_workers))
    for idx, row in arranged_workers[:].iterrows():
        print(row)
        worker_id = idx
        wkr_start = row.w_start
        wkr_end = row.w_end
        w_adt_hrs = row.adt_hrs
#         w_adt_hrs = row.min_hrs
        hrs_to_assign = w_adt_hrs - row.hrs_assigned
#         hrs_to_assign = row.adt_hrs - row.hrs_assigned
        # print('技师 ： %s, 需派单 %2.2f 小时, 现有 %d 个订单 ' %
        #   (idx, hrs_to_assign, len(jobs), ))
#         print(row)
        n = 0
        worker_free_time = sch_workers.get_worker_free_time(worker_id, day_str)
        if worker_free_time is None:
            continue
        for ft in worker_free_time:
            w_start = ft['w_start']
            w_end = ft['w_end']
            while ((w_end - w_start)/np.timedelta64(1, 'm') >= 20) & (hrs_to_assign > 0.5):
                # print('   ...派单中: ', '服务开始时间：' ,w_start, '服务结束时间：', w_end, ' 需派工时',hrs_to_assign,' 当前订单数: ', len(jobs) )

                # n += 1
                # if n > 1:
                #     print(' ### 第 %d 次为技师: %d 分配订单 ###' % (n, worker_id))
                jobs_a = jobs.loc[(jobs.worker_id == 0) & (
                    (jobs.end_time + jobs.hrs_t >= w_start) & (jobs.start_time + jobs.hrs_t <= w_end))]
                # print(len(jobs_a),  'jobs available')
                if len(jobs_a):
                    #: arrange jobs for wrk
                    order_interval = datetime.timedelta(seconds=300)
                    job_arranged = sort_jobs(
                        jobs_a, order_interval, w_start, w_end)
                    if len(job_arranged) > 0:
                        job_grp = job_arranged.groupby(['addr', 'grp']).agg({
                            'hrs': 'sum',
                            'plan_start': 'first',
                            'plan_end': 'last',
                            'trans_hr': 'sum',
                            'wait_hr': 'sum',
                            'order_id': 'count'
                        })

                        job_grp.loc[:, 'duration'] = (
                            job_grp.plan_end - job_grp.plan_start)/np.timedelta64(1, 'h')
                        job_grp.loc[:, 'idle_rate'] = np.where(
                            job_grp.order_id == 1, 0, np.round(job_grp.wait_hr / job_grp.duration, 2)*100)
                        job_grp = job_grp.reset_index().sort_values(
                            ['hrs', 'idle_rate', 'duration', 'plan_start', 'addr', 'grp', ], ascending=[0, 1, 0,  0, 1, 1])

                        # print(' --- %d  job grp find..' % (len(job_grp)))

#                         if len(job_grp) == 0:
#                             print(jobs_a)
#                             print(job_arranged)
#                             print(job_grp)
                        job_grp_a = job_grp[(job_grp.hrs >= hrs_to_assign) & (
                            job_grp.plan_end <= w_end)]

                        if len(job_grp_a) > 0:
                            #: 如果 订单组 时间大于 需派单时间， 找到最适合的订单组, 分解
                            split_start = 0
                            split_end = 0
                            min_hrs = 100
                            for g in job_grp_a.grp:
                                jt = job_arranged[job_arranged.grp == g].sort_values(
                                    'plan_start')
                                for x in range(len(jt)):
                                    jt_s = jt[x:]
                                    jt_s.loc[:, 'hr_sum'] = jt_s.hrs.cumsum(
                                    ) - hrs_to_assign
                                    idx = len(jt_s[jt_s['hr_sum'] <= 0]) + 1
                                    idl_hrs = jt_s[:idx].trans_hr.sum(
                                    ) + jt_s[:idx].wait_hr.sum()
                                    tt_hrs = sum(jt_s[:idx].hrs)
                                    if idl_hrs <= min_hrs and tt_hrs >= hrs_to_assign:
                                        min_hrs = idl_hrs
                                        split_start = x
                                        split_end = x + idx
                                        grp_id = g
                            # print('  截取订单', grp_id, '..','start at:', split_start, ' end.. at:',split_end )
                            grp_addr = job_grp_a.loc[job_grp_a.grp ==
                                                     grp_id].iloc[0].addr
                            jobs_to_assign = job_arranged.loc[job_arranged.grp ==
                                                              grp_id][split_start:split_end]
                        else:
                            #                     print(job_grp)
                            grp_to_assign = job_grp.hrs.nlargest(1)
        #                     print('grp_to_assign', grp_to_assign)
                            grp_addr = job_grp.loc[grp_to_assign.index[0], 'addr']
                            jobs_to_assign = job_arranged[job_arranged.grp ==
                                                          job_grp.loc[grp_to_assign.index[0], 'grp']]
        #                     print('  grp idx to_assign ', grp_to_assign.index[0])

                    list_jobs_to_assign = jobs_to_assign.order_id.tolist()
                    jobs_to_assign.loc[:, 'worker_id'] = worker_id
                    # print('   订单分配成功 ', '地址：', grp_addr, ' 订单编号: ', list_jobs_to_assign, '合计小时数: ', jobs_to_assign.hrs.sum())

                    #: 添加到 已分配订单
                    assigned_jobs = assigned_jobs.append(
                        jobs_to_assign, ignore_index=True)

                    # ：从待分配中移除
                    jobs = jobs[~jobs.order_id.isin(list_jobs_to_assign)]

                    # ：更新技师的待派单时间
    #                 hrs_to_assign = w_adt_hrs - job_grp.loc[grp_to_assign.index[0], 'hrs']
                    hrs_to_assign = hrs_to_assign - jobs_to_assign.hrs.sum()
                    # print('adt_hrs to assign', w_adt_hrs, '',jobs_to_assign.hrs.sum(), hrs_to_assign)
                    if hrs_to_assign <= 0:
                        hrs_to_assign = 0
                    w_start = jobs_to_assign.iloc[-1].plan_end + order_interval

                    # print('     技师还有', (w_end - w_start)/np.timedelta64(1, 'm'), ' 分钟剩余工时... ', w_start, w_end, '还需派单： ', hrs_to_assign)

    #                 if (w_end - w_start)/np.timedelta64(1, 'm') <= -40:
    #                     print(job_grp_a)
                    # print('    ** ' * 10)
    #                 worker_fully_assigned = True
    #                 print(arranged_workers.loc[worker_id])
    #                 print(len(jobs), len(assigned_jobs))
                else:
                    # print('   技师 %2d  工作时段 %2s  ～ %2s  没有订单可分配...' % (worker_id, w_start.time(), w_end.time()))
                    #                 print(jobs.loc[:, ('start_time', 'end_time', 'hrs','order_id')])
                    break

            worker_jobs = assigned_jobs[assigned_jobs.worker_id == worker_id]
            arranged_workers.loc[worker_id,
                                 'hrs_assigned'] = worker_jobs.sum().hrs

            f1 = (row.w_start - worker_jobs.plan_start.min()) / \
                np.timedelta64(1, 'm')
            # print('w-s', row.w_start, worker_jobs.plan_start.min(), worker_jobs.plan_end.max(), row.w_end, f1)

#         print(work_jobs.sort_values(['plan_start'], ascending=[1]))

        # print('派单完成: 技师 ： %s, 需派单 %2.2f 小时, 已派单 %2.2f  小时' % (worker_id, w_adt_hrs, worker_jobs.sum().hrs, ))
        # print('====' * 10)

    # print('完成分配...  %2d 个订单还未分配, %2d 个订单已分配..' %(len(jobs), len(assigned_jobs)))
    worker_summary = assigned_jobs.groupby(['worker_id']).agg({
        'plan_start': 'first',
        'plan_end': 'last',
        'hrs': 'sum',
        'wait_hr': 'sum',
        'order_id': 'count'
    })
    # print(' %2d worker done...' % len(worker_summary))
#     print(worker_summary)
    # print('### 还剩下  %d 个订单未分配 ' % len(jobs))
#     print(jobs)
    return assigned_jobs, jobs, worker_summary, arranged_workers


if __name__ == '__main__':
    jobs.loc[:, 'worker_id'] = 0
    assigned_jobs, open_jobs, worker_summary, arranged_workers = dispatch_region_jobs(
        jobs, workers)
