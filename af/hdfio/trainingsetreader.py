"""
traininsetreader.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("HdfTrainingSetReader", )


import h5py
import numpy as np
from af.hdfio import HdfBaseReader, HdfFileInfo, HdfItem


class HdfTrainingSetReader(HdfBaseReader):

    EXTENSIONS = (".hdf5", ".hdf", ".h5")
    GALLERY_SETTINGS_MUTABLE = False

    _bbox = "/data/bbox"
    _gallery = "/data/gallery"
    _images = "/data/images"
    _contours = "/data/contours"
    _features = "/data/features"

    def __init__(self, filename, mode="r"):
        super(HdfTrainingSetReader, self).__init__()
        self._hdf = h5py.File(filename, mode)

    @property
    def fileinfo(self):

        cspace = self.cspace()
        cspace = {'plate': cspace.keys(),
                  'well': cspace.values()[0].keys(),
                  'site': cspace.values()[0].values()[0].keys(),
                  'region': cspace.values()[0].values()[0].values()[0]}

        return HdfFileInfo(self.GALLERY_SETTINGS_MUTABLE,
                           self.numberItems(), self.gsize, cspace)

    @property
    def gsize(self):
        # default size of a gallery image
        return self._hdf[self._gallery].shape[0]

    # XXX set attributes to hdffile
    def numberItems(self, coordinate=None):
        return self._hdf[self._bbox].shape[0]

    def featureNames(self, region):
        return self._hdf[self._features].dtype.names

    def _get_contours(self, index):

        hsize = np.floor(self.gsize/2.0)

        label, cx, cy, top, bottom, left, right = self._hdf[self._bbox][index]

        cnt = self._hdf[self._contours+"/Channel_1"][index]
        x0 = cnt[0].astype(np.float32)
        y0 = cnt[1].astype(np.float32)
        cnt = np.array([(x-cx+hsize, y-cy+hsize)
                        for x, y in zip(x0, y0)], dtype=np.float32)

        cnt = np.clip(cnt, 0, self.gsize)

        return cnt

    def loadItem(self, index, *args, **kw):
        # x, y, c, stack
        gal = self._hdf[self._gallery][:, :, 0, index]
        cnt = self._get_contours(index)
        ftr = self._hdf[self._features][index]
        objid = self._hdf[self._bbox]["label"][index]
        return HdfItem(gal, cnt, ftr, objid)
