"""
hdfwriter.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import h5py
import numpy as np

class HdfError(Exception):
    pass


class HdfCache(object):
    """Internal cache to be able to save non-resizeable data sets to hdf5."""

    def __init__(self, feature_names, gallery_dtype):

        self.gallery = None
        self.data = None
        self.features = None
        self.contours = list()

        self._dt_gallery = gallery_dtype
        self._dt_data = [('label', np.uint32), ('x', np.uint16),
                         ('y', np.uint16), ('top', np.uint16),
                         ('bottom', np.uint16), ('left', np.uint16),
                         ('right', np.uint16)]

        self._dt_features = [(n, np.float32) for n in feature_names]
        self._dt_contours = h5py.special_dtype(vlen=np.uint16)

    def appendData(self, objectsdict):
        nobj = len(objectsdict)
        nftrs = len(objectsdict.feature_names)

        data = np.empty((nobj, ), dtype=self._dt_data)
        features = np.empty((nobj, ), dtype=self._dt_features)
        gallery = np.empty(objectsdict.gallery_shape, dtype=self._dt_gallery)

        # need to cast to the correct type
        for i, (label, obj) in enumerate(objectsdict.iteritems()):
            data[i] = np.array((label, ) + obj.center + obj.bbox,
                               dtype=self._dt_data)
            features[i] = obj.features.astype(np.float32)
            gallery[:, :, :, i] = obj.gallery_image.astype(np.uint16)
            self.contours.append(np.array(obj.contour, dtype=np.uint16).T)

        if self.data is self.features is self.gallery:
            self.data = data
            self.features = features
            self.gallery = gallery
        else:
            # from PyQt4.QtCore import pyqtRemoveInputHook; pyqtRemoveInputHook()
            # import pdb; pdb.set_trace()

            self.data = np.append(self.data, data)
            self.features = np.append(self.features, features)
            self.gallery = np.concatenate((self.gallery, gallery), axis=3)


class HdfWriter(object):

    IMAGES = "/images"
    CONTOURS = "/contours"
    GALLERY = "/gallery"
    DATA = "/data"
    FEATURES = "/features"

    def __init__(self, filename):
        self._file = h5py.File(filename, "w")
        self._cache = None

    def close(self, flush=True):
        if flush:
            self.flush()
        self._file.close()

    def setupImages(self, n_images, n_channels, size, dtype):
        shape = size + (n_channels, n_images)
        self.images = self._file.create_dataset(self.IMAGES, shape, dtype=dtype)

    def setImage(self, image, index):
        self.images[:, :, :, index] = image

    def saveData(self, objectsdict):

        if self._cache is None:
            self._cache = HdfCache(objectsdict.feature_names,
                                   objectsdict.gallery_dtype)
        self._cache.appendData(objectsdict)

    def flush(self):

        # hdf5 allows only 64kb of header metadata
        try:
            dset = self._file.create_dataset(
                self.DATA, data=self._cache.data)
            dset = self._file.create_dataset(
                self.FEATURES, data=self._cache.features)
            dset = self._file.create_dataset(
                self.GALLERY, data=self._cache.gallery)
            dset = self._file.create_dataset(
                self.CONTOURS, data=self._cache.contours,
                dtype=self._cache._dt_contours)
        except ValueError as e:
            if "Object header message is too large" in str(e):
                raise HdfError("Cannot save data to hdf file."
                                 "One of you tables is to large, "
                                 "reduce number of channels")
