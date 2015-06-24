"""
seeding.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import numpy as np
from scipy import ndimage


def normalize_image(image):
    """Normalize an image to a range 0-1 (float) for ploting with matplotlib."""

    if image.dtype == np.dtype('bool'):
        return image

    try:
        iinfo = np.iinfo(image.dtype)
        range_ = iinfo.max - iinfo.min
        return image/float(range_)
    except ValueError:
        return (image - image.min())/(image.ptp())


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


def find_seeds(img_edt, size=5):


    img_lmax = ndimage.filters.maximum_filter(img_edt, size)
    img_lmax = ndimage.filters.gaussian_filter(img_lmax, size/1.5)
    lmax_x, lmax_y = local_maxima(img_lmax, size, 0.001)

    seeds = np.zeros(img_edt.shape, dtype=bool)
    seeds[lmax_y, lmax_x] = True
    seeds, _ = ndimage.measurements.label(seeds)
    return seeds, lmax_x, lmax_y


def seed_mask(label_image, seeds):
    # seeds image has not the same labeling, the position counts
    seed_labels = np.unique(label_image*seeds.astype(bool))
    labels = np.unique(label_image)
    nlabels = np.setdiff1d(labels, seed_labels)

    for nl in nlabels:
        label_image[label_image == nl] = 0

    return label_image.astype(bool)
