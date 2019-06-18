# -*- coding: utf-8 -*-
# @Time    : 4/15/19 5:16 PM
# @Author  : dbchan
# @File    : cluster_address.py
# @Software: PyCharm

from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
import numpy as np


def cluster(X):
    """

    :param X:np.array([[lat0,lon0],[lat1,lon1],[lat2,lon2]...])
    :return:labels
    """
    # Compute Affinity Propagation
    af = AffinityPropagation().fit(X)
    # cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    lat_label = [str(round(af.cluster_centers_[i][0], 5)) + '-' +
                 str(round(af.cluster_centers_[i][1], 5)) for i in af.labels_]

    # n_clusters_ = len(cluster_centers_indices)
    # data = {}
    # try:
    #     for k in range(n_clusters_):
    #         lump_data = []
    #         # cluster_center = X[cluster_centers_indices[k]]
    #         # cen = {'cen': {'lng': cluster_center[0], 'lat': cluster_center[1]}}
    #         class_members = labels == k
    #         for i in X[class_members].tolist():
    #             lump_data.append({'lng': i[0], 'lat': i[1]})
    #         # lump_data.append(cen)
    #         data[str(k)] = lump_data

    return labels, lat_label


if __name__ == '__main__':
    list_a = []
    n = 0
    i = np.random.randint(5152, 5676, 20)
    s = 121 + i / 10000
    j = np.random.randint(114963, 159883, 20)
    m = 31 + j / 1000000
    while n < 20:
        # print(n)
        l = [s[n], m[n]]
        n += 1
        list_a.append(l)
    # print(list_a)
    X = np.array(list_a)
    print(cluster(X))
