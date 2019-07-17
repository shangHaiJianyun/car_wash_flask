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
