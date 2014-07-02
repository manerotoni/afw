"""
readercore.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("HdfBaseReader", "HdfError", "HdfItem", "HdfFileInfo",
           "HdfAttrNames")

from collections import namedtuple

import numpy as np
from qimage2ndarray import gray2qimage

from PyQt4.QtGui import QColor

from af.pattern import Factory
from af.gui.painting import AfPainter


HdfFileInfo = namedtuple("HdfFileInfo",
                         ["gal_settings_mutable", "n_items", "gallery_size",
                          "coordspace"])


class HdfAttrNames(object):

    colors = "colors"
    channels = "channels"


class HdfError(Exception):
    pass


class HdfItem(object):

    __slots__ = ['image', 'contour', 'features', 'frame', 'objid', 'colors']

    def __init__(self, image, contour, features, objid=None, frame=None,
                 colors=None):
        self.image = image
        self.contour = contour
        self.features = features
        self.frame = frame
        self.objid = objid

        if image.ndim == 2: # gray image
            self.colors = ["#ffffff"]
        elif colors is None:
            self.colors = image.shape[2]*[str("#ffffff")]
        else:
            self.colors = colors

    def __str__(self):
        return "%d-%d" %(self.frame, self.objid)

    def iterQImages(self):
        """Iterator over qimages (indexed_8) with colortable set."""

        iinfo = np.iinfo(self.image.dtype)
        ncolors = abs(iinfo.max - iinfo.min)
        for i, color in enumerate(self.colors):
            lut = AfPainter.lut_from_color(QColor(color), ncolors)
            if self.image.ndim == 2:
                image = gray2qimage(self.image, normalize=True)
            else:
                image = gray2qimage(self.image[:, :, i], normalize=True)
            image.setColorTable(lut)
            yield image

    def pixmap(self):
        # XXX be aware of thread safety
        images = list(self.iterQImages())
        return AfPainter.blend(images)

    def iterContours(self):
        for i, color in enumerate(self.colors):
            yield self.contour[i], QColor(color)


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
