"""
normalize.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import numpy as np

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
