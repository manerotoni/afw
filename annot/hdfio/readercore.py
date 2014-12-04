"""
readercore.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("HdfFile", "HdfError", "HdfItem", "HdfFileInfo")


import h5py
import numpy as np
from collections import namedtuple

from qimage2ndarray import gray2qimage
from PyQt4.QtGui import QColor

from annot.pattern import Factory
from annot.gui.painting import AtPainter


HdfFileInfo = namedtuple("HdfFileInfo",
                         ["gal_settings_mutable", "n_items", "gallery_size",
                          "coordspace"])


class HdfError(Exception):
    pass


class HdfItem(object):

    __slots__ = ['image', 'contour', 'features', 'index', 'frame',
                 'objid', 'colors', 'hash']

    def __init__(self, image, contour, features, index, objid=None, frame=None,
                 colors=None):
        self.image = image
        self.contour = contour
        self.features = features
        self.index = index
        self.frame = frame
        self.objid = objid

        if image.ndim == 2: # gray image
            self.colors = ["#ffffff"]
        elif colors is None:
            self.colors = image.shape[2]*[str("#ffffff")]
        else:
            self.colors = colors

        self.hash = hash(tuple(zip(*contour)))

    def __eq__(self, other):
        return self.hash == other.hash

    def __str__(self):
        return "%d-%d" %(self.frame, self.objid)

    def iterQImages(self):
        """Iterator over qimages (indexed_8) with colortable set."""

        iinfo = np.iinfo(self.image.dtype)
        ncolors = abs(iinfo.max - iinfo.min)
        for i, color in enumerate(self.colors):
            lut = AtPainter.lut_from_color(QColor(color), ncolors)
            if self.image.ndim == 2:
                image = gray2qimage(self.image, normalize=False)
            else:
                image = gray2qimage(self.image[:, :, i], normalize=False)
            image.setColorTable(lut)
            yield image

    def pixmap(self):
        # XXX be aware of thread safety
        images = list(self.iterQImages())
        return AtPainter.blend(images)

    def iterContours(self):
        for i, color in enumerate(self.colors):
            yield self.contour[i], QColor(color)


class HdfFile(h5py.File):

    __metaclass__ = Factory
    GALLERY_SETTINGS_MUTABLE = True

    # h5py file modes
    READWRITE = "r+"
    READONLY = "r"
    WRITE = "w"
    WRITEFAIL = "w-"
    READWRITECREATE = "a"

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
