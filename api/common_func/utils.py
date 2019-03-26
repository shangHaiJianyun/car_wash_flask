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

from math import cos, sin, sqrt, pi, tan, atan2


class GetLocation(object):
    """
    大地坐标系资料WGS - 84
    长半径a = 6378137
    短半径b = 6356752.3142
    扁率f = 1 / 298.2572236
    """
    # 长半径a = 6378137
    _a = 6378137
    # 短半径b = 6356752.3142
    _b = 6356752.3142
    # 扁率f = 1 / 298.2572236
    _f = 1 / 298.2572236

    def __init__(self, lon, lat, brng, dis):
        self.lon = lon
        self.lat = lat
        self.brng = brng
        self.dis = dis

    def rad(self, d):
        # 将度换成弧度
        return d * pi / 180.0

    def deg(self, x):
        # 将弧度换成度
        return x * 180 / pi

    def calculate_loc(self):
        alpha1 = self.rad(self.brng)
        sinAlpha1 = sin(alpha1)
        cosAlpha1 = cos(alpha1)

        tanU1 = (1 - self._f) * tan(self.rad(self.lat))
        cosU1 = 1 / sqrt((1 + tanU1 * tanU1))
        sinU1 = tanU1 * cosU1
        sigma1 = atan2(tanU1, cosAlpha1)
        sinAlpha = cosU1 * sinAlpha1
        cosSqAlpha = 1 - sinAlpha * sinAlpha
        uSq = cosSqAlpha * (self._a * self._a - self._b * self._b) / (self._b * self._b)
        A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - 175 * uSq)))
        B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - 47 * uSq)))

        cos2SigmaM = 0
        sinSigma = 0
        cosSigma = 0
        sigma = self.dis / (self._b * A)
        sigmaP = 2 * pi
        while abs(sigma - sigmaP) > 1e-12:
            cos2SigmaM = cos(2 * sigma1 + sigma)
            sinSigma = sin(sigma)
            cosSigma = cos(sigma)
            deltaSigma = B * sinSigma * (cos2SigmaM + B / 4 * (cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)
                                                               - B / 6 * cos2SigmaM * (-3 + 4 * sinSigma * sinSigma) * (
                                                                       -3 + 4 * cos2SigmaM * cos2SigmaM)))
            sigmaP = sigma
            sigma = self.dis / (self._b * A) + deltaSigma

        tmp = sinU1 * sinSigma - cosU1 * cosSigma * cosAlpha1
        lat2 = atan2(sinU1 * cosSigma + cosU1 * sinSigma * cosAlpha1,
                     (1 - self._f) * sqrt(sinAlpha * sinAlpha + tmp * tmp))
        amb = atan2(sinSigma * sinAlpha1, cosU1 * cosSigma - sinU1 * sinSigma * cosAlpha1)
        C = self._f / 16 * cosSqAlpha * (4 + self._f * (4 - 3 * cosSqAlpha))
        L = amb - (1 - C) * self._f * sinAlpha * (
                sigma + C * sinSigma * (cos2SigmaM + C * cosSigma * (-1 + 2 * cos2SigmaM * cos2SigmaM)))
        # revAz = atan2(sinAlpha, -tmp)
        # print(revAz)

        return self.lon + self.deg(L), self.deg(lat2)


if __name__ == '__main__':
    loc = GetLocation(121.62486, 29.87816, 90, 5000)
    s = loc.calculate_loc()
    print(s[0], s[1])
