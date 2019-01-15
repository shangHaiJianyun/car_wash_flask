1.

- [ ] 用户登录接口：dev.upctech.com.cn/api/user/login

- [ ] 请求方式：POST

- [ ] 请求参数几返回值说明：

  |                  | 参数名                                                       | 类型 | 说明           |
  | ---------------- | ------------------------------------------------------------ | :--: | -------------- |
  | 输入参数         | username                                                     | str  | 用户名         |
  |                  | password                                                     | str  | 密码           |
  


2.

- [ ] 用户登出接口：dev.upctech.com.cn/api/user/logout

- [ ] 请求方式：GET

- [ ] 返回信息：成功：

  {
  ​    "message": "user logout"
  }



3.

- [ ] 更新用户信息接口：dev.upctech.com.cn/api/user/update_info

- [ ] 请求方式：POST

- [ ] 请求参数及返回值：

  请求参数（json）:

  ```python
  {
  	"name":"edison",
  	"email":"12345@abc.com",
  	"mobile":"13324560973"
  }
  ```

  返回值：

  ```python
  {
      "UnionID": null,
      "active": true,
      "created_on": "2018-12-18 06:11:02",
      "email": "12345@abc.com",
      "id": 5,
      "mobile": "13324560973",
      "modified_on": "2018-12-18 06:59:57",
      "name": "edison",
      "password": "$2b$12$bN2.bh5NRGyBWhX109WxnubxUOmEDDvgZyUYfMySQVfJc9NbdW5sK",
      "username": "18355090212",
      "wxName": null,
      "wxid": null,
      "wxpicurl": null,
      "xcxid": null
  }
  ```


4.

- [ ] 进入管理员界面：dev.upctech.com.cn/api/user/test

- [ ] 请求方式:GET

- [ ] 认证方式：

  ```python
  HEADERS：{
      Authorization:Bearer 'token'
  }
  ```



5.

- [ ] 获取用户地址价格系数接口： dev.upctech.com.cn/api/map/get_rate

- [ ] 请求方式：POST

- [ ] 请求参数及返回值说明：

  |                  | 参数名                                                       | 类型    | 说明             |
  | ---------------- | ------------------------------------------------------------ | ------- | ---------------- |
  | 传入参数（json） | lng                                                          | 字符串  | 经度             |
  |                  | lat                                                          | 字符串  | 纬度             |
  | 传入参数示例     | {"lng": 120.572,
    "lat": 30.620843}                        | json    |                  |
  | 输出参数         | rate_name                                                    | string  | 该地区的价格组   |
  |                  | rate_level                                                   | float   | 该地区的价格系数 |
  |                  | area_name                                                    | striing | 该地区所属城市   |
  |                  | city_code                                                    | string  | 该地区的区域     |
  | 输出参数示例     | {
<br/>    "area_name": "上海市",
    "city_code": "200000",
    "rate_level": 3,
    "rate_name": "三等"
} |         |                  |



6.

- [ ] 车牌识别接口：dev.upctech.com.cn/api/lpr/lpr

- [ ] 请求方式：POST

- [ ] 请求参数及返回值说明：


|            | 参数名                 | 类型      | 说明           |
| ---------- | ---------------------- | --------- | -------------- |
| 输入参数   | file                   | form-data | 带有车牌的照片 |
| 输出参数   | lp                     | str       | 车牌号         |
- [ ]  返回值示例 

  ```python
  {
      "lp": "京EL0662"
  } 
  ```

  



7.

- [ ] 短信验证码获取接口：dev.upctech.com.cn/api/utils/verify_mobile/string:phone/

- [ ] 请求方式：GET

- [ ] 返回值示例：

  ```python
  {
      "code": "3780"
  }
  ```
