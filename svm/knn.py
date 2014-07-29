"""
knn.py

Calculate the average distance of a point and its k-nearest neighbors
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ["dist_knn"]

import numpy as np


def dist_knn(data, k=5):

    dist = list()
    for i, x in enumerate(data):
        d = np.sqrt(((data-x)**2).sum(axis=0))
        d.sort()
        d = d[1:k+1]
        dist.extend(d)
    return np.mean(dist)
