## 项目一  car_wash 

#### 公司后台使用的api接口

##### 1.用户

###### 1> dev.upctech.com.cn/api/user/login    POST/json   用户登陆



```json
{
	"username":"admin",
	"password":"123"
}

```

###### 2> dev.upctech.com.cn/api/user/logout   GET   用户登出

###### 3> dev.upctech.com.cn/api/user/update_info    POST/json  修改用户信息

```json
{
	"name":"edison",
	"email":"12345@abc.com",
	"mobile":"13324560973"
}


```

##### 2.地图分区信息

###### 1> dev.upctech.com.cn/api/map/map_data  GET   地图分区信息显示

###### 2> dev.upctech.com.cn/api/map/get_rate  POST/json   根据经纬度来获取所属区域信息及level

```json
input:
{
	"lat": 31.204399, 
	"lng": 121.429627
}
output:
{
    "area_id": 439,
    "city": "上海市",
    "city_code": "200000",
    "rate_level": 1,
    "rate_name": "一等"
}
```

###### 3> dev.upctech.com.cn/api/map/get_nearby  POST/json  根据区域id获取周边5公里的区域信息

```json
input:
{
	"area_id":137
}
output:
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
    "dr": {
        "area_cen": {
            "lat": 31.092503,
            "lng": 120.965
        },
        "area_id": 166,
        "area_name": "上海市青浦区朱家角镇听湖别苑淀山湖风景区",
        "distance": 16383,
        "ridding_time": 3932
    },
    "ll": {},
    "rr": {
        "area_cen": {
            "lat": 31.137423,
            "lng": 120.965
        },
        "area_id": 167,
        "area_name": "江苏省苏州市昆山市锦溪镇淀山湖风景区",
        "distance": 14975,
        "ridding_time": 3594
    },
    "ul": {},
    "ur": {},
    "uu": {}
}
```



##### 3.操作php端接口

###### 1> dev.upctech.com.cn/api/dis/getworklist  POST/json  获取技师列表

```json
{
	"city":"上海市"
}
```

###### 2> dev.upctech.com.cn/api/dis/getorderlist   GET  获取订单列表

###### 3> dev.upctech.com.cn/api/dis/updateOrderStatus   POST/json  修改订单状态

```json
{
	"order_ids":"7558",
	"order_status":2
}
```

###### 4> dev.upctech.com.cn/api/dis/getItemlist   POST/json  获取洗车服务项目

```json
{
	"city":"上海市"
}
```

###### 5>dev.upctech.com.cn/api/dis/getOrderDetail    POST/json  获取订单详情

```json
{
	"order_no":"2019040215031013209723"
}
```

###### 6>dev.upctech.com.cn/api/dis/getMemberList   POST/json  获取用户列表详情

```json
{
	"city":"上海市"
}
```

###### 7>dev.upctech.com.cn/api/dis/getDispatchOrderList  POST/json  获取用户已派单的列表信息

```json
{
	"uid":672,
	"dispatch_type":1
}
```

##### 4.派单测试接口

###### 1>  dev.upctech.com.cn/api/sch/get_sim_data     POST/json    生成 测试 的 worker 和 job 数据

```json
{
	"workday":"2019-04-12",
	"n_order":20,
	"n_address":3,
	"regions":[135,137,437,438]
}
```

###### 2> dev.upctech.com.cn/api/sch/show_schedule_task  POST/json  展示派单任务

```json
{
	"city":"上海市"
}
```

###### 3> dev.upctech.com.cn/api/sch/sch_today   GET  派今日的单

###### dev.upctech.com.cn/api/sch/sch_result   GET 派明日订单





#### 提供给php端的接口

###### 1> dev.upctech.com.cn/api/map/rate  POST/json  根据区域id获取区域系数

```json
input:
{
	"area_id":24
}
output:
{
    "area_rate": 1
}
```



###### 2> dev.upctech.com.cn/api/map/lpr/lpr    POST/form-data  车牌识别

```form-data
file：选取的图片
```


#### car_wash中的func

###### 1>api/common_func

- area.py ：与数据库中地图数据操作相关func
- city_code.py ：定义城市编码及区域系数
- cluster_address.py：坐标聚类func
- decorators.py：定义了用户角色认证的func
- near_by.py：定义区域周边信息的func
- tx_to_bd.py：定义了腾讯地图坐标转换成百度地图坐标的func
- utils.py：GetLocation：根据坐标和距离获取指定坐标；get_ride：坐标与坐标的路径规划耗时和行程信息;

###### 2> api/modules/scheduler：派单系统中使用到的func及api

- sch.py
- sch_api.py
- sch_lib.py
- sch_sim.py