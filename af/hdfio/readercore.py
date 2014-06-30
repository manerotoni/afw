"""
readercore.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("HdfBaseReader", "HdfError", "HdfTrainingSetReader", "HdfItem",
           "HdfFileInfo")


import h5py
import numpy as np
from collections import namedtuple
from af.pattern import Factory


HdfFileInfo = namedtuple("HdfFileInfo",
                         ["gal_settings_mutable", "n_items", "gallery_size",
                          "coordspace"])


class HdfError(Exception):
    pass


class HdfItem(object):

    __slots__ = ['image', 'contour', 'features', 'frame', 'objid']

    def __init__(self, image, contour, features, objid=None, frame=None):
        self.image = image
        self.contour = contour
        self.features = features
        self.frame = frame
        self.objid = objid

    def __str__(self):
        return "%d-%d" %(self.frame, self.objid)


class HdfBaseReader(object):

    __metaclass__ = Factory
    GALLERY_SETTINGS_MUTABLE = True

    @classmethod
    def readers(cls):
        return cls._classes.keys()

    @property
    def fileinfo(self):
        """Determines the default number of items to load (cellh5 files
        contain to many items to load them at once) and wether the size of
        the gallery images is fixed. This method must be implemented
        by child classes."""
        raise NotImplementedError()

    def close(self):
        self._hdf.close()

    def plateNames(self):
        return ["---"]

    def wellNames(self, coords):
        return ["---"]

    def siteNames(self, coords):
        return ["---"]

    def regionNames(self):
        return ["---"]

    def cspace(self):
        """Returns a full mapping of the coordiante space the hdf file"""

        # plate, well and site point to one single movie. each movie
        # can have different segementation regions.

        coord = dict()
        coorddict = dict()
        plates = self.plateNames()
        regions = self.regionNames()

        for plate in plates:
            coord['plate'] = plate
            wells = self.wellNames(coord)
            coorddict.setdefault(plate, {})
            for well in wells:
                coord['well'] = well
                coorddict[plate].setdefault(well, {})
                sites = self.siteNames(coord)
                for site in sites:
                    coorddict[plate][well][site] = regions
        return coorddict



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


        return cnt

    def loadItem(self, index, *args, **kw):
        # x, y, c, stack
        gal = self._hdf[self._gallery][:, :, 0, index]
        cnt = self._get_contours(index)
        ftr = self._hdf[self._features][index]
        objid = self._hdf[self._bbox]["label"][index]
        return HdfItem(gal, cnt, ftr, objid)
