# -*- coding: utf-8 -*-
# @Time    : 4/15/19 5:16 PM
# @Author  : dbchan
# @File    : cluster_address.py
# @Software: PyCharm

from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
import numpy as np


# Generate sample data
# centers = [[1, 1], [-1, -1], [1, -1]]
# X, labels_true = make_blobs(n_samples=200, centers=3, cluster_std=0.5,
#                             random_state=0)


def cluster(X):
    # Compute Affinity Propagation
    af = AffinityPropagation().fit(X)
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_
    n_clusters_ = len(cluster_centers_indices)
    data = {}
    try:
        for k in range(n_clusters_):
            lump_data = []
            cluster_center = X[cluster_centers_indices[k]]
            cen = {'cen': {'lng': cluster_center[0], 'lat': cluster_center[1]}}
            class_members = labels == k
            for i in X[class_members].tolist():
                lump_data.append({'lng': i[0], 'lat': i[1]})
            lump_data.append(cen)
            data[str(k)] = lump_data

        return data
    except:
        return {"error": "Unable to clustering"}


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
    print(list_a)
    X = np.array(list_a)
    cluster(X)
