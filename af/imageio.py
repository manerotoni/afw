"""
imageio.py

Read Zeiss LSM files and split them into cellcognition compatible slices
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import numpy as np
from pylsm.lsmreader import Lsmimage


class ImageProps(object):
    """Describes basic image data types. It determines min/max grey values
    ranges and the bitdepth."""


    __slots__ = ["image_min", "image_max", "min", "max", "range", "bitdepth",
                 "histogram"]

    def __init__(self, image):

        self.image_min = image.min()
        self.image_max = image.max()

        if np.issubdtype(np.int, image.dtype) or \
                np.issubdtype(np.uint, image.dtype):
            iinfo = np.iinfo(image.dtype)
            self.min = iinfo.min
            self.max = iinfo.max
            self.range = self.max - self.min
            self.histogram = np.histogram(image.flatten(), bins=self.range)

        elif np.issubdtype(np.float, image.dtype):
            finfo = np.finfo(image.dtype)
            self.min = 0.0
            self.max = 1.0
            self.range = 1.0
            self.histogram = np.histogram(image.flatten(), bins=256)
        self.bitdepth = np.nbytes[image.dtype]*8


class MetaData(object):
    """Meta data of an image, such as size, number of channels its dtype.
    Furhter ther is the number of images which is similar to the stack size.
    """

    __slot__ = ["size", "dtype", "nchannels", "n_images"]

    def __init__(self, size, n_channels, dtype, n_images=None):
        self.size = size
        self.n_channels = n_channels
        self.dtype = dtype
        self.n_images = n_images

    @property
    def image_dimension(self):
        return self.size + (self.n_channels, )


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
        self.open()

    def iterprops(self):
        for ci in xrange(self.channels):
            yield ImageProps(self.get_image(stack=0, channel=ci))

    @property
    def metadata(self, nfiles=None):
        return MetaData(self.size, self.channels, self.dtype)

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

    def toArray(self, channels=None, stack=0):

        if channels is None:
            channels = range(self.channels)

        image = np.zeros(self.size + (len(channels), ), dtype=self.dtype)
        for i, ci in enumerate(channels):
            image[:, :, i] = self.get_image(stack=stack, channel=ci)
        return image
