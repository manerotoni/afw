"""
traininsetreader.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("HdfTrainingSetReader", )


import h5py
import numpy as np
from af.hdfio import HdfBaseReader, HdfFileInfo, HdfItem, HdfAttrNames


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

        channels = self._hdf[self._contours].attrs[HdfAttrNames.channels]
        contours = list()

        for channel in channels:
            cnt = self._hdf[self._contours+"/%s" %channel][index]
            x0 = cnt[0].astype(np.float32)
            y0 = cnt[1].astype(np.float32)
            cnt = np.array([(x-cx+hsize, y-cy+hsize)
                            for x, y in zip(x0, y0)], dtype=np.float32)

            cnt = np.clip(cnt, 0, self.gsize)
            contours.append(cnt)

        return contours

    def loadItem(self, index, *args, **kw):
        # x, y, c, stack
        cols = self._hdf[self._images].attrs[HdfAttrNames.colors]
        cols = [str(c) for c in cols] # no unicode
        gal = self._hdf[self._gallery][:, :, :, index]
        cnts = self._get_contours(index)
        ftr = self._hdf[self._features][index]
        objid = self._hdf[self._bbox]["label"][index]
        return HdfItem(gal, cnts, ftr, objid, frame=0, colors=cols)
