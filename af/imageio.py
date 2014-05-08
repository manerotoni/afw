"""
imageio.py

Read Zeiss LSM files and split them into cellcognition compatible slices
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import numpy as np
from pylsm.lsmreader import Lsmimage


class LsmImage(Lsmimage):
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
        return (self.header[self.CZ_LSM_INFO][self.WIDTH],
                self.header[self.CZ_LSM_INFO][self.HEIGHT])

    @property
    def channels(self):
        return self.header[self.IMAGE][0][self.CHANNEL]

    def iterQImages(self):
        for ci in self.channels:
            yield array2qimage(lsm.get_image(stack=0, channel=ci))
