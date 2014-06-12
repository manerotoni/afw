"""
multicolor.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('MultiChannelProcessor', 'LsmProcessor')


import warnings
import numpy as np
from collections import OrderedDict

from qimage2ndarray import gray2qimage
from cecog import ccore
from cecog.environment import CecogEnvironment

from af.imageio import LsmImage
from af.segmentation import ObjectDict, ImageObject


class MultiChannelProcessor(object):

    _environ = CecogEnvironment(redirect=False, debug=False)

    def __init__(self, filename, gallery_size=50):
        super(MultiChannelProcessor, self).__init__()

        self._image = None
        self._reader = None
        self._filename = filename
        self.gsize = gallery_size
        self._containers = OrderedDict()

    @property
    def metadata(self):
        return self._reader.metadata

    def iterprops(self):
        return self._reader.iterprops()

    @property
    def image(self):
        if self._image is None:
            self._image = self._reader.toArray()
        return self._image

    @image.deleter
    def image(self):
        del self._image

    def iterQImages(self, all_channels=True):
        """Iterator over to qimage converted images, one qimage per channel."""
        if all_channels:
            channels = range(self._reader.channels)
        else:
            channels = self.channels.keys()

        for ci in channels:
            yield gray2qimage(self._reader.get_image(stack=0, channel=ci),
                              normalize=False)

    def _gallery_image(self, center, gallery_size=50):
        height, width, nchannels = self.image.shape
        halfsize = np.floor(gallery_size/2.0)

        xmin = center.x - halfsize
        xmax = xmin + gallery_size
        ymin = center.y - halfsize
        ymax = ymin + gallery_size

        if xmin < 0:
            xmin = 0
            xmax = gallery_size
        elif xmax >= width:
            xmin = width - gallery_size
            xmax = width

        if ymin < 0:
            ymin = 0
            ymax = gallery_size
        elif ymax >= height:
            ymin = height - gallery_size
            ymax = height

        gimg = self.image[ymin:ymax, xmin:xmax, self._channel_idx]
        return gimg

    @property
    def objects(self):
        odict = ObjectDict("multicolor")
        for i, (name, container) in enumerate(self._containers.iteritems()):
            for label, cobj in container.getObjects().iteritems():
                obj = ImageObject(name, cobj,
                                  container.getCrackCoordinates(label), label)

                if odict.has_key(label):
                    odict.concatenate(name, label, obj)
                else:
                    # mulitchannel gallery image
                    obj.gallery_image = self._gallery_image(obj.center,
                                                            gallery_size=50)
                    odict[label] = obj

            # set feature names extend with a prefix
            odict.feature_names.extend(
                ["c%d-%s" %(i, n) for n in obj.feature_names])

        removed = odict.remove_incomplete()
        if len(removed) > 0:
            warnings.warn("%d objects have been removed" %len(removed))
        return odict

    def calculateFeatures(self, feature_groups):
        """Calculate the features per color channel."""
        # assert set(feature_groups.keys()) == set(self.cnames)

        for name, container in self._containers.iteritems():
            fgroups = feature_groups[name]
            for group, params in fgroups.iteritems():
                if params is None:
                    container.applyFeature(group)
                else: # special case for haralick features
                    for param in params:
                        container.haralick_distance = param
                        container.applyFeature(group)

    def segmentation(self, params, channels, master_channel=0):
        assert isinstance(params, dict)
        assert isinstance(master_channel, int)

        # neede for gallery images
        self._channel_idx = channels.keys()

        # segment the master first
        cname = channels[master_channel]
        image = self.image[:, :, master_channel].copy()
        self._containers[cname] = self.threshold(image, *params[cname])
        label_image = self._containers[cname].img_labels.toArray()

        for i, name in channels.iteritems():
            if i == master_channel:
                continue
            self._containers[name] = self.seededExpandedRegion(
                self.image[:, :, i].copy(), label_image, *params[name])

    def threshold(self, image, mean_radius, window_size, min_contrast,
                  remove_borderobjects, fill_holes):

        image = ccore.numpy_to_image(image, copy=True)
        image = ccore.disc_median(image, mean_radius)

        seg_image = ccore.window_average_threshold(
            image, window_size, min_contrast)

        if fill_holes:
            ccore.fill_holes(seg_image)

        return ccore.ImageMaskContainer(image, seg_image,
                                        remove_borderobjects)

    def seededExpandedRegion(self, image, label_image, srg_type, label_number,
                             region_statistics_array=0,
                             expansion_size=1,
                             sep_expansion_size=0):

        if label_number is None:
           label_number = label_image.max() + 1

        image = ccore.numpy_to_image(image, copy=True)
        limage = ccore.numpy_to_image(label_image, copy=True)

        img_labels = ccore.seeded_region_expansion(image, limage,
                                                   srg_type,
                                                   label_number,
                                                   region_statistics_array,
                                                   expansion_size,
                                                   sep_expansion_size)

        return ccore.ImageMaskContainer(image, img_labels, False, True, True)


class LsmProcessor(MultiChannelProcessor):

    def __init__(self, filename, gallery_size=50):
        super(LsmProcessor, self).__init__(filename, gallery_size)
        self._reader = LsmImage(filename)
