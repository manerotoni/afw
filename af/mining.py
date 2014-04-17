"""
mining.py

Collection of various helper functions
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import numpy as np


def filter_nans(data, data2=None):
    """Delete columns from that contain NAN's"""

    nans = np.isnan(data)
    col_nans = np.unique(np.where(nans)[1])
    if data2 is None:
        return np.delete(data, col_nans, axis=1)
    else:
        return (np.delete(data, col_nans, axis=1),
                np.delete(data2, col_nans, axis=1))
