"""
imageio.py

Read Zeiss LSM files and split them into cellcognition compatible slices
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import numpy as np
from pylsm.lsmreader import Lsmimage

class ImageProps(object):
    """Describes basic image data types. It determines min/max grey values
    ranges and the bitdepth."""


    __slots__ = ["image_min", "image_max", "min", "max", "range", "bitdepth",
                 "histogram"]

    def __init__(self, image):

        self.image_min = image.min()
        self.image_max = image.max()
        self.bitdepth = np.nbytes[image.dtype]*8

        if np.issubdtype(np.int, image.dtype) or \
                np.issubdtype(np.uint, image.dtype):
            iinfo = np.iinfo(image.dtype)
            self.min = iinfo.min
            self.max = iinfo.max
            bins = range(2**self.bitdepth)
            self.histogram = np.histogram(image.flatten(), bins=bins)

        elif np.issubdtype(np.float, image.dtype):
            finfo = np.finfo(image.dtype)
            self.min = 0.0
            self.max = 1.0
            self.histogram = np.histogram(image.flatten(), bins=256)
            self.hist_minmax = self.histogram

    @property
    def range(self):
        return np.array([self.min, self.max])

    def autoRange(self, value=0.1):
        """Return minimum and maximum values of an image that cut of 1 percent of
        the image histogram
        """

        hist = self.histogram[0]
        csum = hist.cumsum()
        npixels = csum[-1]
        hmin = npixels*value*0.005 # 0.5 % of the pixes
        hmax = npixels - hmin

        try:
            maximum = min(csum[csum <= hmax].size, hist.size - 1)
        except ValueError:
            maximum = self.image_max

        try:
            minimum = max(csum[csum <= hmin].size - 1, 0)
        except ValueError:
            minimum = self.image_min

        return np.array((minimum, maximum))

    @property
    def dynamic_range(self):
        return np.array([self.image_min, self.image_max])


class MetaData(object):
    """Meta data of an image, such as size, number of channels its dtype.
    Furhter ther is the number of images which is similar to the stack size.
    """

    __slot__ = ["size", "dtype", "nchannels", "n_images"]

    def __init__(self, size, n_zslices, n_channels, dtype, n_images=None):
        self.size = size
        self.n_channels = n_channels
        self.dtype = dtype
        self.n_images = n_images
        self.n_zslices = n_zslices

    @property
    def image_dimension(self):
        return self.size + (self.n_channels, )
