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
from .imageio import ImageProps, MetaData


class TiffImage(object):

    _Order = ('x', 'y', 'z', 'c')
    Idx_x = 0
    Idx_y = 1
    Idx_z = 2
    Idx_c = 3

    def __init__(self, filename):
        # vigra does not talk in unicode
        filename = str(filename)

        info = vigra.impex.ImageInfo(filename)

        shape  = info.getShape()
        if len(shape)  > 4:
            raise RuntimeError("5d images are not supported")

        self._dtype = info.getDtype()
        image = vigra.impex.readVolume(filename, dtype=self._dtype)

        # correct the axestags
        axistags = info.getAxisTags()
        for at in image.axistags:
            if at not in axistags:
                axistags.append(at)
        self._image = self._swap2xyzc(image, axistags)
        self._shape = self._image.shape

    def _swap2xyzc(self, image, axistags):
        """Swap axes of the array that it follows the convention xyzc"""

        target = (vigra.AxisInfo.x, vigra.AxisInfo.y,
                  vigra.AxisInfo.z, vigra.AxisInfo.c)

        target_idx =  [axistags.index(t) for t in self._Order]

        for i, j in enumerate(target_idx):
            print i, j
            if i != j and i < j:
                image = image.swapaxes(i, j)

        return image

    def iterprops(self):
        for ci in xrange(self.channels):
            yield ImageProps(self.get_image(stack=0, channel=ci))

    @property
    def metadata(self, nfiles=None):
        return MetaData(self.size, self.channels, self.dtype)

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

    def toArray(self, channels=None, stack=0):
        if channels is None:
            channels = range(self.channels)

            image = np.zeros(self.size + (len(channels), ), dtype=self.dtype)
        for i, ci in enumerate(channels):
            image[:, :, i] = self.get_image(stack=stack, channel=ci)
        return image

    def get_image(self, stack=0, channel=0):
        return self._image[:, :, stack, channel].transposeToNumpyOrder()
