"""
imagereader.py

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('ImageReader', )

from .imageio import ImageProps, MetaData

class ImageReader(object):
    """Mixin class for Image reader interface.
    """

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

    def get_image(self, *args, **kw):
        raise NotImplementedError()

    def iterprops(self):
        for ci in xrange(self.channels):
            yield ImageProps(self.get_image(stack=0, channel=ci))

    @property
    def metadata(self, nfiles=None):
        return MetaData(self.size, self.channels, self.dtype)

    def toArray(self, channels=None, stack=0):

        if channels is None:
            channels = range(self.channels)

        image = np.zeros(self.size + (len(channels), ), dtype=self.dtype)
        for i, ci in enumerate(channels):
            image[:, :, i] = self.get_image(stack=stack, channel=ci)
        return image
