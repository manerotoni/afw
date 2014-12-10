"""
seeding.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import numpy as np
from scipy import ndimage
from normalize import normalize_image


def local_maxima(data, size, threshold=0.01):

    data = normalize_image(data)

    data_max = ndimage.filters.maximum_filter(data, size)
    maxima = (data == data_max)
    data_min = ndimage.filters.minimum_filter(data, size)
    diff = ((data_max - data_min) > threshold)
    maxima[diff == 0] = 0

    labeled, num_objects = ndimage.label(maxima)
    slices = ndimage.find_objects(labeled)
    x, y = [], []
    for dy, dx in slices:
        x_center = (dx.start + dx.stop - 1)/2
        x.append(x_center)
        y_center = (dy.start + dy.stop - 1)/2
        y.append(y_center)

    return x, y


def find_seeds(img_edt):

    img_lmax = ndimage.filters.maximum_filter(img_edt, 5)
    img_lmax = ndimage.filters.gaussian_filter(img_lmax, 5)
    lmax_x, lmax_y = local_maxima(img_lmax, 5, 0.01)

    seeds = np.zeros(img_edt.shape, dtype=bool)
    seeds[lmax_y, lmax_x] = True
    seeds, _ = ndimage.measurements.label(seeds)
    return seeds, lmax_x, lmax_y
