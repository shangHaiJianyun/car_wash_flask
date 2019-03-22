# -*- coding: utf-8 -*-
# @Time    : 19-1-11 上午9:47
# import datetime
# import time
#
#
# def compareTime(service_date):
#     time_array = time.strptime(service_date, "%Y-%m-%d")
#     service_time = time.mktime(time_array)
#     acquire = datetime.date.today() + datetime.timedelta(days=2)
#     tomorrow_end_time = int(time.mktime(time.strptime(str(acquire), '%Y-%m-%d'))) - 1
#     today = datetime.date.today()
#     today_time = int(time.mktime(today.timetuple()))
#
#     # print(service_time, now)
#     if today_time <= service_time < tomorrow_end_time:
#         return True
#     else:
#         return False
