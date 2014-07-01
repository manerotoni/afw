"""
hdfwriter.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('HdfWriter', )


import h5py
import numpy as np
from collections import defaultdict
from af.hdfio import HdfAttrNames

class HdfCache(object):
    """Internal cache to be able to save non-resizeable data sets to hdf5."""

    def __init__(self, feature_names, gallery_dtype):

        self.gallery = None
        self.bbox = None
        self.features = None
        self.contours = defaultdict(list)

        self._dt_gallery = gallery_dtype
        self._dt_bbox = [('label', np.uint32), ('x', np.uint16),
                         ('y', np.uint16), ('top', np.uint16),
                         ('bottom', np.uint16), ('left', np.uint16),
                         ('right', np.uint16)]

        self._dt_features = [(n, np.float32) for n in feature_names]
        self._dt_contours = h5py.special_dtype(vlen=np.uint16)

    def appendData(self, objectsdict):
        nobj = len(objectsdict)
        nftrs = len(objectsdict.feature_names)

        bbox = np.empty((nobj, ), dtype=self._dt_bbox)
        features = np.empty((nobj, ), dtype=self._dt_features)
        gallery = np.empty(objectsdict.gallery_shape, dtype=self._dt_gallery)

        # need to cast to the correct type
        for i, (label, obj) in enumerate(objectsdict.iteritems()):
            bbox[i] = np.array((label, ) + obj.center + obj.bbox,
                               dtype=self._dt_bbox)
            features[i] = obj.features.astype(np.float32)
            gallery[:, :, :, i] = obj.gallery_image.astype(np.uint16)

            for cname, contour in obj.contours.iteritems():
                self.contours[cname].append((np.array(contour).T).tolist())

        if self.bbox is self.features is self.gallery:
            self.bbox = bbox
            self.features = features
            self.gallery = gallery
        else:
            self.bbox = np.append(self.bbox, bbox)
            self.features = np.append(self.features, features)
            self.gallery = np.concatenate((self.gallery, gallery), axis=3)


class HdfWriter(object):

    DATA = "/data"
    IMAGES = "/data/images"
    CONTOURS = "/data/contours"
    GALLERY = "/data/gallery"
    BBOX = "/data/bbox"
    FEATURES = "/data/features"

    def __init__(self, filename):
        self._file = h5py.File(filename, "w")
        self._cache = None

    def close(self):
        self._file.close()

    def setupFile(self, n_images, channels, colors, size, dtype):
        n_channels = len(channels)
        shape = size + (n_channels, n_images)

        grp = self._file.create_group(self.CONTOURS)
        grp.attrs[HdfAttrNames.channels] = [str(c.replace(" ", "_"))
                                             for c in channels.values()]

        self.images = self._file.create_dataset(self.IMAGES, shape, dtype=dtype)
        self.images.attrs[HdfAttrNames.colors] = [str(c) for c in colors]

    def setImage(self, image, index):
        self.images[:, :, :, index] = image

    def saveData(self, objectsdict):
        # sometimes there are not objects found in an image
        # and objectsdict is empty
        if objectsdict:
            if self._cache is None:
                self._cache = HdfCache(objectsdict.feature_names,
                                       objectsdict.gallery_dtype)
            self._cache.appendData(objectsdict)

    def _write_contours(self):

        for cname, contours in self._cache.contours.iteritems():
            path = "%s/%s" %(self.CONTOURS, cname.replace(" ", "_"))

            # h5py seems to be buggy, cannot set contours directly,
            dset = self._file.create_dataset(
                path, (len(contours), 2, ), dtype=self._cache._dt_contours)
            for i, cnt in enumerate(contours):
                dset[i, :] = cnt


    def flush(self):

        # hdf5 allows only 64kb of header metadata
        try:
            dset = self._file.create_dataset(
                self.BBOX, data=self._cache.bbox)
            dset = self._file.create_dataset(
                self.FEATURES, data=self._cache.features)
            dset = self._file.create_dataset(
                self.GALLERY, data=self._cache.gallery)
            self._write_contours()
        except ValueError as e:
            if "Object header message is too large" in str(e):
                raise HdfError("Cannot save data to hdf file."
                                 "One of you tables is to large, "
                                 "reduce number of channels")
