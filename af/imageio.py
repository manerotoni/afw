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
    def zslices(self):
        return self.header[self.CZ_LSM_INFO][self.ZSTACK]

    @property
    def size(self):
        return (self.header[self.CZ_LSM_INFO][self.WIDTH],
                self.header[self.CZ_LSM_INFO][self.HEIGHT])

    @property
    def channels(self):
        return self.header[self.IMAGE][0][self.CHANNEL]

    # def meta_images(self, channel):
    #     """Get a list of cellcognition meta images for a given channel.
    #     One meta image per z-slice"""
    #     assert isinstance(channel, int)

    #     if not (0 <= channel < self.channels):
    #         raise RuntimeError("channel %d does not exist" %channel)

    #     metaimages = list()
    #     for i in xrange(self.zslices):
    #         img = self.get_image(stack=i, channel=channel)
    #         # kinda sucks, but theres no way around
    #         metaimage = MetaImage()
    #         metaimage.set_image(ccore.numpy_to_image(img, copy=True))
    #         metaimages.append(metaimage)
    #     return metaimages
