"""
tiff.py

Reader for 4d tif files.

5d image will raise an exception.
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('TiffImage', )


import vigra
import numpy as np
from .imagecore import ImageCore

XYC = vigra.AxisTags(vigra.AxisInfo.x, vigra.AxisInfo.y,
                     vigra.AxisInfo.c)
XYZC = vigra.AxisTags(vigra.AxisInfo.x, vigra.AxisInfo.y,
                      vigra.AxisInfo.z, vigra.AxisInfo.c)

class TiffImage(ImageCore):

    def __init__(self, filename):
        # vigra does not talk in unicode
        filename = str(filename)

        info = vigra.impex.ImageInfo(filename)

        shape  = info.getShape()
        if len(shape)  > 4:
            raise RuntimeError("5d images are not supported")

        self._dtype = info.getDtype()
        image = vigra.impex.readImage(filename, dtype=self._dtype)

        if info.getAxisTags() == XYC:
            self._image = np.expand_dims(image.transposeToNumpyOrder(), axis=2)
        elif info.getAxisTags() == XYZC:
            self._image = image

        self._shape = self._image.shape

    @property
    def bitdepth(self):
        types = {np.uint8: 8,
                 np.uint16: 16,
                 np.uint32: 32}
        return types[self._dtype]

    @property
    def dtype(self):
        return self._dtype

    @property
    def zSlices(self):
        return self._shape[self.Idx_z]

    @property
    def size(self):
        return self._shape[self.Idx_x], self._shape[self.Idx_y]

    @property
    def channels(self):
        return self._shape[self.Idx_c]

    def get_image(self, stack=0, channel=0):
        if isinstance(self._image, np.ndarray):
            return self._image[:, :, stack, channel]
        else:
            return self._image[:, :, stack, channel].transposeToNumpyOrder()
