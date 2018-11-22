# doc
ttc backend project

## structure

api  
  |--- api.py:  wxapi 页面和接口
  |--- controllers
          |----- 业务相关的类
  |--- templates
          |---- 页面模版


models: models


## commands

本地服务器
`python manage.py runserver`

命令行模式 
`python manage.py shell`


初始化数据库 
`python manage.py db init `

数据库升级
`python manage.py db migrate `
`python manage.py db upgrade `
