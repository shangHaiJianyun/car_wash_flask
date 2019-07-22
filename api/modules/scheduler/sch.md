# 订单派单和模拟

## 步骤

1.  创建模拟订单

    > @sch_blu.route('/get_sim_data', methods=['POST'])

    - data:

    ```javascript
    { "workday": "2019-07-18", "n_worker":5, "n_address":10, "n_order": 20, "regions": [438, 439, 440] }
    ```

    - 提供上述参数，系统创建 订单，工人数据

2 自动派单模拟

        > @sch_blu.route('/sch_simulate', methods=['POST'])


        ```javascript
        {
        "city": "上海市",
        "sch_date":"2019-07-18"
        }

        ```


    - 调用 sch_sim.py 下的  start_multi_region_sch(）

        > 每次自动创建新的 Sch_Task, 将系统中未分配订单，标记 sch_task_id


        > 异步方式： 可以调用   api.new_task 下的 region_job_sch()

        > 非异步方式： 调用 sch_dim.py 下的  sch_tomorrow_by_region

    - 流程：

        > 目前派单 不包括特服 (worker_type = 3  )
        > 先对每个区域派单

        > 所有区域派单完成后， 对剩余订单

            - 找到 区域 临近区域的工人，派单

        > Todo： 最后剩余的 未派单 （worker_id = '0')  派给  特服 (worker_type = 3  )

3.  显示 派单的 Task

        > @sch_blu.route('/show_schedule_task', methods=['GET'])

        无参数

4)  Reset Task

    将 已派单的 订单 set 为 NUll， 可以重新派单 > @sch_blu.route('/reset_schedule_task', methods=['GET'])

        ```shell
            127.0.0.1:5000/api/sch/reset_schedule_task?sch_task_id=118

        ```

## 按时间段统计 workload

按时间段统计 workloda 可以 用 pandas resample

以下示例 输入的 数据 都是 pandas dataframe

> sch_lib 下的 SchJobs 和 SchWorker 的方法，返回的数据 如果是 df 就是 dataframe

> 注意： df 中，plan_start 等时间数据，用的 是 timestamp， 需要转成 str 才能 jsonsify

            ```python

                #： datetime 字符转 timestamp

                df.loc[:, 'w_start'] = pd.to_datetime(df.w_start, format="%Y-%m-%d %H:%M")

                #： df  输出 json ， 或保存到 db 前， 转换为 str
                assigned_jobs.plan_start = assigned_jobs.plan_start.apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))

            ```

```python

def cal_region_order_req(region_jobs, period, bucket='start_time'):
    '''
        按 period 计算需求工时
        bucket: 'start_time' 或 'plan_start'
    '''
    region_jobs = region_jobs.set_index(bucket)
    region_req = region_jobs.resample(period).agg({
        'addr': 'last',
        'order_id': 'count',
        'hrs': 'sum'
    })
    region_req = region_req.rename(columns={'order_id': 'num_orders', 'hrs': 'req_hrs'})
    return region_req


def cal_region_wrk_hrs(region_wkrs, period):
    d = region_wkrs.iloc[0].w_start.date().isoformat()
    hrs_idx = pd.date_range(d + ' 6:00', d + ' 22:00', freq=period)
    hrs_bucket = pd.DataFrame(columns=['wrks', 'wrk_hrs'], index=hrs_idx).fillna(0)
    for idx, row in region_wkrs.iterrows():
        wh_idx = pd.date_range(row.w_start, row.w_end, freq = '1h')
        w_bucket = pd.DataFrame(columns=['wrks', 'wrk_hrs'], index=wh_idx).fillna(1)
        hrs_bucket = hrs_bucket.join(w_bucket, rsuffix = '_').fillna(0)
        hrs_bucket.loc[:,'wrks'] = hrs_bucket.wrks + hrs_bucket.wrks_
        hrs_bucket.loc[:,'wrk_hrs'] = hrs_bucket.wrk_hrs + hrs_bucket.wrk_hrs_
        hrs_bucket = hrs_bucket.drop(['wrks_', 'wrk_hrs_'], 1)
    hrs_bucket = hrs_bucket.resample(period).agg({'wrks': 'mean', 'wrk_hrs': 'sum'})
    return hrs_bucket

def calculate_region_loads(region_id,jobs, workers, period, bucket='start_time'):
    region_req = cal_region_order_req(jobs, period, bucket)
    region_wrk_hrs = cal_region_wrk_hrs(workers, period)
    region_req_supply = region_wrk_hrs.join(region_req).fillna(0)
    region_req_supply.loc[:, 'region_id'] = region_id
    region_req_supply.loc[:, 'short_hrs'] = region_req_supply.wrk_hrs - region_req_supply.req_hrs
    return region_req_supply


period = '1h'
region_id = 3
region_req_supply = calculate_region_loads(region_id, jobs, workers, period)

```
