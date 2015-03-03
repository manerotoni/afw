"""
imageio.py

Read Zeiss LSM files and split them into cellcognition compatible slices
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('LsmImage', )


import numpy as np
from pylsm.lsmreader import Lsmimage
from .imagecore import ImageCore

class LsmImage(ImageCore, Lsmimage):
    """LSM image class to fit the needs of the classfinder plugin.
    i.e. it has methods to return the number of channels, z-slices etc...
    """

    CZ_LSM_INFO = 'CZ LSM info'
    WIDTH = 'Dimension X'
    HEIGHT = 'Dimension Y'
    ZSTACK = 'Dimension Z'
    CHANNEL = 'Sample / Pixel'
    IMAGE = 'Image'
    BITDEPTH = 'Bit / Sample'

    def __init__(self, *args, **kw):
        Lsmimage.__init__(self, *args, **kw)
        self.open()

    @property
    def bitdepth(self):
        return self.header[self.IMAGE][0][self.BITDEPTH]

    @property
    def dtype(self):
        types = {8: np.uint8,
                 16: np.uint16,
                 32: np.uint32}
        return types[self.bitdepth]

    @property
    def zSlices(self):
        return self.header[self.CZ_LSM_INFO][self.ZSTACK]

    @property
    def size(self):
        return (self.header[self.CZ_LSM_INFO][self.HEIGHT],
                self.header[self.CZ_LSM_INFO][self.WIDTH])

    @property
    def channels(self):
        return self.header[self.IMAGE][0][self.CHANNEL]

    def get_image(self, *args, **kw):
        image = Lsmimage.get_image(self, *args, **kw)
        # pylsm does not get the strides right
        byteoffset = self.bitdepth/8
        image.strides =  (byteoffset, image.shape[0]*byteoffset)
        return image.swapaxes(0, 1)
