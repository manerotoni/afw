"""
imagereader.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('ImageCore', )

import numpy as np
from .imageio import ImageProps, MetaData


class ImageCore(object):

    _Order = ('x', 'y', 'z', 'c')
    Idx_x = 0
    Idx_y = 1
    Idx_z = 2
    Idx_c = 3

    def iterprops(self):
        for ci in xrange(self.channels):
            yield ImageProps(self.get_image(stack=0, channel=ci))

    @property
    def metadata(self):
        return MetaData(self.size, self.zSlices, self.channels, self.dtype)

    @property
    def bitdepth(self):
        raise NotImplementedError()

    @property
    def dtype(self):
        raise NotImplementedError()

    @property
    def zSlices(self):
        raise NotImplementedError()

    @property
    def size(self):
        raise NotImplementedError()
    @property
    def channels(self):
        raise NotImplementedError()

    def toArray(self, channels=None, stack=None):

        if channels is None:
            channels = range(self.channels)

        if stack is None:
            stack = range(self.zSlices)

        if np.max(stack) > self.zSlices or np.min(stack) < 0:
            raise RuntimeError("Invalid stack parameter")

        # convention: xyzc
        image = np.zeros(self.size + (len(stack), len(channels), ),
                         dtype=self.dtype)
        for j in stack:
            for i, ci in enumerate(channels):
                image[:, :, j, i] = self.get_image(stack=j, channel=ci)
        return image

    def get_image(self, *args, **kw):
        raise NotImplementedError()
