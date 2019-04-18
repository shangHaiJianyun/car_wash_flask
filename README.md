# Role_allocate
car_sch

1.POSTMAN接口Doc：
   
      https://documenter.getpostman.com/view/5990473/RznJmcEB

2.celery的配置信息在config.py文件中

   启动celery的命令：
   
       celery worker -A api.celery_tasks.tasks --loglevel=info

       celery -A api.celery_tasks.tasks:celery worker -l info -B (包含定时任务时的终端命令)
    
    

3.获取区域周边的信息接口为：
     
     dev.upctech.com.cn/api/map/get_nearby
  
  
  1>post参数：
        
        {"area_id":<int>}
        
  2>返回数据信息：
        
        {
            "dd": {
                "area_cen": {
                    "lat": 31.092503,
                    "lng": 120.9126
                },
                "area_id": 136,
                "area_name": "上海市青浦区金泽镇湖头村",
                "distance": 7101,
                "ridding_time": 1704
            },
            "dl": {},
            "dr": {},
            "ll": {},
            "rr": {},
            "ul": {},
            "ur": {},
            "uu": {}
        }
