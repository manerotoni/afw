"""
hdfwriter.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import h5py
import numpy as np


class HdfWriter(object):

    IMAGES = "/images"
    CONTOURS = "/contours"
    FEATURES = "/features"
    GALLERIES = "/galleries"
    ROI = "/roi"

    def __init__(self, filename):
        self._file = h5py.File(filename, "w")

    def close(self):
        self._file.close()

    def setupImages(self, n_images, n_channels, size, dtype):
        shape = size + (n_channels, n_images)
        self.images = self._file.create_dataset(self.IMAGES, shape, dtype=dtype)

    def setImage(self, image, index):
        self.images[:, :, :, index] = image

    def saveData(self, objectsdict):
        for label, obj in objectsdict.iteritems():
            print label, obj.bbox, obj.gallery_image.shape
