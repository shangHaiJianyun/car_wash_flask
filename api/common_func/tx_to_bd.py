# -*- coding: utf-8 -*-
# @Time    : 5/20/19 9:19 AM
# @Author  : dbchan
# @Software: PyCharm
from math import sqrt, sin, atan2, cos


def convert(lat, lon):
    x_pi = 3.14159265358979324
    z = sqrt(lat * lat + lon * lon) + 0.00002 * sin(lat * x_pi)
    theta = atan2(lat, lon) + 0.000003 * cos(lon * x_pi)
    db_lon = z * cos(theta) + 0.0065
    bd_lat = z * sin(theta) + 0.006
    return bd_lat, db_lon


if __name__ == '__main__':
    print(convert(121.429627, 31.204399))
